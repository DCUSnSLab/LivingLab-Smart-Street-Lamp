#include "led-matrix.h"
#include "graphics.h"

#include <getopt.h>
#include <math.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>


#include <exception>
#include <Magick++.h>
#include <magick/image.h>

using namespace rgb_matrix;
using rgb_matrix::Canvas;
using rgb_matrix::RGBMatrix;
using rgb_matrix::FrameCanvas;

// Make sure we can exit gracefully when Ctrl-C is pressed.
volatile bool interrupt_received = false;
static void InterruptHandler(int signo) {
  interrupt_received = true;
}

using ImageVector = std::vector<Magick::Image>;

// Given the filename, load the image and scale to the size of the
// matrix.
// // If this is an animated image, the resutlting vector will contain multiple.
static ImageVector LoadImageAndScaleImage(const char *filename,
                                          int target_width,
                                          int target_height) {
  ImageVector result;

  ImageVector frames;
  try {
    readImages(&frames, filename);
  } catch (std::exception &e) {
    if (e.what())
      fprintf(stderr, "%s\n", e.what());
    return result;
  }

  if (frames.empty()) {
    fprintf(stderr, "No image found.");
    return result;
  }

  // Animated images have partial frames that need to be put together
  if (frames.size() > 1) {
    Magick::coalesceImages(&result, frames.begin(), frames.end());
  } else {
    result.push_back(frames[0]); // just a single still image.
  }

  for (Magick::Image &image : result) {
    image.scale(Magick::Geometry(target_width, target_height));
  }

  return result;
}


// Copy an image to a Canvas. Note, the RGBMatrix is implementing the Canvas
// interface as well as the FrameCanvas we use in the double-buffering of the
// animted image.
void CopyImageToCanvas(const Magick::Image &image, Canvas *canvas) {
  const int offset_x = 0, offset_y = 0;  // If you want to move the image.
  // Copy all the pixels to the canvas.
  for (size_t y = 0; y < image.rows(); ++y) {
    for (size_t x = 0; x < image.columns(); ++x) {
      const Magick::Color &c = image.pixelColor(x, y);
      if (c.alphaQuantum() < 256) {
        canvas->SetPixel(x + offset_x, y + offset_y,
                         ScaleQuantumToChar(c.redQuantum()),
                         ScaleQuantumToChar(c.greenQuantum()),
                         ScaleQuantumToChar(c.blueQuantum()));
      }
    }
  }
}

// An animated image has to constantly swap to the next frame.
// We're using double-buffering and fill an offscreen buffer first, then show.
void ShowAnimatedImage(const ImageVector &images, RGBMatrix *matrix) {
  FrameCanvas *offscreen_canvas = matrix->CreateFrameCanvas();
  while (!interrupt_received) {
    for (const auto &image : images) {
      if (interrupt_received) break;
      CopyImageToCanvas(image, offscreen_canvas);
      offscreen_canvas = matrix->SwapOnVSync(offscreen_canvas);
      usleep(image.animationDelay() * 10000);  // 1/100s converted to usec
    }
  }
}

int image_usage(const char *progname) {
  fprintf(stderr, "Usage: %s [led-matrix-options] <image-filename>\n",
          progname);
  rgb_matrix::PrintMatrixFlags(stderr);
  return 1;
}

static int usage(const char *progname) {
  fprintf(stderr, "usage: %s [options]\n", progname);
  fprintf(stderr, "Reads text from stdin and displays it. "
          "Empty string: clear screen\n");
  fprintf(stderr, "Options:\n");
  fprintf(stderr,
          "\t-f <font-file>    : Use given font.\n"
          "\t-x <x-origin>     : X-Origin of displaying text (Default: 0)\n"
          "\t-y <y-origin>     : Y-Origin of displaying text (Default: 0)\n"
          "\t-S <spacing>      : Spacing pixels between letters (Default: 0)\n"
          "\t-C <r,g,b>        : Color. Default 255,255,0\n"
          "\t-B <r,g,b>        : Font Background-Color. Default 0,0,0\n"
          "\t-O <r,g,b>        : Outline-Color, e.g. to increase contrast.\n"
          "\t-F <r,g,b>        : Panel flooding-background color. Default 0,0,0\n"
          "\n"
          );
  rgb_matrix::PrintMatrixFlags(stderr);
  return 1;
}

static bool parseColor(Color *c, const char *str) {
  return sscanf(str, "%hhu,%hhu,%hhu", &c->r, &c->g, &c->b) == 3;
}

static bool FullSaturation(const Color &c) {
  return (c.r == 0 || c.r == 255)
    && (c.g == 0 || c.g == 255)
    && (c.b == 0 || c.b == 255);
}

int main(int argc, char *argv[]) {
  Magick::InitializeMagick(*argv);

  // Initialize the RGB matrix with
  RGBMatrix::Options matrix_options;
  rgb_matrix::RuntimeOptions runtime_opt;
  if (!rgb_matrix::ParseOptionsFromFlags(&argc, &argv,
                                         &matrix_options, &runtime_opt)) {
    return image_usage(argv[0]), usage(argv[0]);
  }

  char line[1024] = {0,};
  char *temp, *ptr;
  int num;
  int mul, sum; // var for 'ptr' type change  
  int len;  // length of 'ptr' string
  char tmp; // var for line count
  int line_cnt = 0; // number of lines (in txt file)

  Color color(255, 255, 255);
  Color bg_color(0, 0, 0);
  Color flood_color(0, 0, 0);
  Color outline_color(0,0,0);
  bool with_outline = false;

  const char *bdf_font_file = NULL;
  int x_orig = 0;
  int y_orig = 0;
  int letter_spacing = 0;


  /* count number of lines (in txt file) */
  FILE *fp_; 
  fp_ = fopen("imagetest.txt", "r");

  while(fscanf(fp_, "%c", &tmp) != EOF) {
    if(tmp == '\n')
      line_cnt++;
  } 
  printf("line_cnt : %d\n", line_cnt);

  fclose(fp_);


  /* start main */
  FILE *fp; 
  fp = fopen("imagetest.txt", "r");

  int opt;
  while ((opt = getopt(argc, argv, "x:y:f:C:B:O:S:F:")) != -1) {
    switch (opt) {
    case 'x': x_orig = atoi(optarg); break;
    case 'y': y_orig = atoi(optarg); break;
    case 'f': bdf_font_file = strdup(optarg); break;
    case 'S': letter_spacing = atoi(optarg); break;
    case 'C':
      if (!parseColor(&color, optarg)) {
        fprintf(stderr, "Invalid color spec: %s\n", optarg);
        return usage(argv[0]);
      }
      break;
    case 'B':
      if (!parseColor(&bg_color, optarg)) {
        fprintf(stderr, "Invalid background color spec: %s\n", optarg);
        return usage(argv[0]);
      }
      break;
    case 'O':
      if (!parseColor(&outline_color, optarg)) {
        fprintf(stderr, "Invalid outline color spec: %s\n", optarg);
        return usage(argv[0]);
      }
      with_outline = true;
      break;
    case 'F':
      if (!parseColor(&flood_color, optarg)) {
        fprintf(stderr, "Invalid background color spec: %s\n", optarg);
        return usage(argv[0]);
      }
      break;
    default:
      return usage(argv[0]);
    }
  }

  if (bdf_font_file == NULL) {
    fprintf(stderr, "Need to specify BDF font-file with -f\n");
    return usage(argv[0]);
  }

  rgb_matrix::Font font;
  if (!font.LoadFont(bdf_font_file)) {
    fprintf(stderr, "Couldn't load font '%s'\n", bdf_font_file);
    return 1;
  }

  rgb_matrix::Font *outline_font = NULL;
  if (with_outline) {
    outline_font = font.CreateOutlineFont();
  }

 
  /* read down each text line(one by one) */

  for(int j = 0; j < line_cnt; j++) {

      int x = x_orig; // 0
      int y = y_orig; // 0

      fgets(line, sizeof(line), fp); // save one line in 'line'
      temp = strtok(line, ","); // character slice
      ptr = strtok(NULL, ",");  // number slice (include front space)


      // type of 'ptr' change(string > int)
      len = strlen(ptr);
      len -= 1;
      sum = 0;
      mul = 1;
      for(int i = 0; i < len - 1; i++) {  
        num = (int) ptr[len - i - 1] - '0';
        sum += (num * mul);
        printf("sum process : %d\n", sum);
        mul *= 10;
      }

    // check each var
    printf("temp:%s\nptr:%ssum:%d\n", temp, ptr, sum);

    color.r = 255;
    color.g = 255;
    color.b = 255;

    RGBMatrix *canvas = RGBMatrix::CreateFromOptions(matrix_options, runtime_opt);
    if (canvas == NULL)
      return 1;

    const bool all_extreme_colors = (matrix_options.brightness == 100)
      && FullSaturation(color)
      && FullSaturation(bg_color)
      && FullSaturation(outline_color);
    if (all_extreme_colors)
      canvas->SetPWMBits(1);

    canvas->Fill(flood_color.r, flood_color.g, flood_color.b);

    const size_t last = strlen(ptr);
    if (last > 0) ptr[last - 1] = '\0';  // remove newline.
    bool line_empty = strlen(ptr) == 0;
    if ((y + font.height() > canvas->height()) || line_empty) {
      canvas->Fill(flood_color.r, flood_color.g, flood_color.b);
      y = y_orig;
    }

    // print temp(char part);

    if(strcmp(temp, "VOC") == 0) {  // done
      rgb_matrix::DrawText(canvas, font, 20, 14,
                        color, outline_font ? NULL : &bg_color, "VOC",
                        letter_spacing);
    }

    else if(strcmp(temp, "CO2") == 0) { // done
      rgb_matrix::DrawText(canvas, font, 1, 14,
                        color, outline_font ? NULL : &bg_color, "이산화탄소",
                        letter_spacing);
    }
    
    else if(strcmp(temp, "HUM") == 0) { // done
      rgb_matrix::DrawText(canvas, font, 20, 14,
                        color, outline_font ? NULL : &bg_color, "습도",
                        letter_spacing);
      strcat(ptr, "%");
    }

    else if(strcmp(temp, "TEMP") == 0) {  // done
      rgb_matrix::DrawText(canvas, font, 21, 14,
                        color, outline_font ? NULL : &bg_color, "기온",
                        letter_spacing);
      strcat(ptr, "°C");
      // strcat(ptr, "℃");
    }

    else if(strcmp(temp, "FINE")==0) {  // done
          rgb_matrix::DrawText(canvas, font, 7, 14,
                        color, outline_font ? NULL : &bg_color, "미세먼지",
                        letter_spacing);

          if(sum >= 0 && sum <= 30) {
              color.r = 0;
              color.g = 0;
              color.b = 255;
          }
          else if(sum >= 31 && sum <= 50) {
              color.r = 0;
              color.g = 255;
              color.b = 0;
          }
          else if(sum >= 51 && sum <= 100) {
              color.r = 255;
              color.g = 255;
              color.b = 0;
          }
          else if(sum >= 101) {
              color.r = 255;
              color.g = 0;
              color.b = 0;
          }
    }

    else if(strcmp(temp, "ULTRA")==0) { // done
          rgb_matrix::DrawText(canvas, font, 1, 14,
                        color, outline_font ? NULL : &bg_color, "초미세먼지",
                        letter_spacing);

          if(sum >= 0 && sum <= 15) {
              color.r = 0;
              color.g = 0;
              color.b = 255;
          }
          else if(sum >= 16 && sum <= 25) {
              color.r = 0;
              color.g = 255;
              color.b = 0;
          }
          else if(sum >= 26 && sum <= 50) {
              color.r = 255;
              color.g = 255;
              color.b = 0;
          }
          else if(sum >= 51) {
              color.r = 255;
              color.g = 0;
              color.b = 0;
          }
    }

    // print ptr(number part)
    printf("strlen = %d\n", strlen(ptr));

    if(strlen(ptr) == 2) {
      rgb_matrix::DrawText(canvas, font, 25, 29,
                        color, outline_font ? NULL : &bg_color, ptr,
                        letter_spacing);
    }

    else if(strlen(ptr) == 3) {
      rgb_matrix::DrawText(canvas, font, 19, 29,
                        color, outline_font ? NULL : &bg_color, ptr,
                        letter_spacing);
    }

    else if(strlen(ptr) == 4) {
      rgb_matrix::DrawText(canvas, font, 16, 29,
                        color, outline_font ? NULL : &bg_color, ptr,
                        letter_spacing);
    }

    else if(strlen(ptr) == 5) {
      rgb_matrix::DrawText(canvas, font, 14, 29,
                        color, outline_font ? NULL : &bg_color, ptr,
                        letter_spacing);
    }

    else {
      rgb_matrix::DrawText(canvas, font, 10, 29,
                        color, outline_font ? NULL : &bg_color, ptr,
                        letter_spacing);
    }

    sleep(3);
    canvas->Clear();
    delete canvas;
  }

  fclose(fp);


  /* print clock */
  color.r = 255;
  color.g = 255;
  color.b = 255;

  time_t timer;
  char timeNow[10] = {'0', '0', ':', '0', '0', ' ', ' ', ' ', ' ', ' '};
  struct tm* t;
  timer = time(NULL);
  t = localtime(&timer);

  int hour = t->tm_hour;
  int min = t->tm_min;

    printf("hour : %d / min : %d\n", hour, min);

  int hour10 = (int) hour / 10;
  int hour1 = hour % 10;
  int min10 = (int) min / 10;
  int min1 = min % 10;

  timeNow[0] = (char) hour10 + '0';
  timeNow[1] = (char) hour1 + '0';
  timeNow[3] = (char) min10 + '0';
  timeNow[4] = (char) min1 + '0';

  RGBMatrix *canvas = RGBMatrix::CreateFromOptions(matrix_options, runtime_opt);
    if (canvas == NULL)
      return 1;

    const bool all_extreme_colors = (matrix_options.brightness == 100)
      && FullSaturation(color)
      && FullSaturation(bg_color)
      && FullSaturation(outline_color);
    if (all_extreme_colors)
      canvas->SetPWMBits(1);

    canvas->Fill(flood_color.r, flood_color.g, flood_color.b);

    rgb_matrix::DrawText(canvas, font, 17, 21,
                          color, outline_font ? NULL : &bg_color, timeNow,
                          letter_spacing);
                        
      sleep(3);
      canvas->Clear();
      delete canvas;

  return 0;
}