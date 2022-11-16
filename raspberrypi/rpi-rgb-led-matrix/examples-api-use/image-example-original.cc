// -*- mode: c++; c-basic-offset: 2; indent-tabs-mode: nil; -*-
//
// Example how to display an image, including animated images using
// ImageMagick. For a full utility that does a few more things, have a look
// at the led-image-viewer in ../utils
//
// Showing an image is not so complicated, essentially just copy all the
// pixels to the canvas. How to get the pixels ? In this example we're using
// the graphicsmagick library as universal image loader library that
// can also deal with animated images.
// You can of course do your own image loading or use some other library.
//
// This requires an external dependency, so install these first before you
// can call `make image-example`
//   sudo apt-get update
//   sudo apt-get install libgraphicsmagick++-dev libwebp-dev -y
//   make image-example

#include "led-matrix.h"

#include <math.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#include <exception>
#include <Magick++.h>
#include <magick/image.h>

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

int usage(const char *progname) {
  fprintf(stderr, "Usage: %s [led-matrix-options] <image-filename>\n",
          progname);
  rgb_matrix::PrintMatrixFlags(stderr);
  return 1;
}

int main(int argc, char *argv[]) {
  Magick::InitializeMagick(*argv);

  // Initialize the RGB matrix with
  RGBMatrix::Options matrix_options;
  rgb_matrix::RuntimeOptions runtime_opt;
  if (!rgb_matrix::ParseOptionsFromFlags(&argc, &argv,
                                         &matrix_options, &runtime_opt)) {
    return usage(argv[0]);
  }

  const char *filename; // file name of image (to print on matrix)
  char line[1024] = {0,};
  char *temp, *ptr;
  int num;
  int mul, sum; // var for 'ptr' type change  
  int len;  // length of 'ptr' string
  char tmp; // var for line count
  int line_cnt = 0; // number of lines (in txt file)


  // count number of lines (in txt file)
  FILE *fp_; 
  fp_ = fopen("imagetest.txt", "r");

  while(fscanf(fp_, "%c", &tmp) != EOF) {
    if(tmp == '\n')
      line_cnt++;
  } 
  printf("line_cnt : %d\n", line_cnt);

  fclose(fp_);


  // read down each text line(one by one)
  FILE *fp; 
  fp = fopen("imagetest.txt", "r");

  for(int j = 0; j < line_cnt; j++) {
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

      // check each line (whether temp == FINE)
      if(strcmp(temp, "FINE")==0) { 
          if(sum >= 0 && sum <= 30) {
              filename = "fine_good.ppm";
              printf("%s\n", filename);
          }
          else if(sum >= 31 && sum <= 50) {
              filename = "fine_normal.ppm";
              printf("%s\n", filename);
          }
          else if(sum >= 51 && sum <= 100) {
              filename = "fine_bad.ppm";
              printf("%s\n", filename);
          }
          else if(sum >= 101) {
              filename = "fine_sobad.ppm";
              printf("%s\n", filename);
          }
      }

      // check each line (whether temp == ULTRA)
      else if(strcmp(temp, "ULTRA")==0) {
          if(sum >= 0 && sum <= 15) {
              filename = "ultra_good.ppm";
          }
          else if(sum >= 16 && sum <= 25) {
              filename = "ultra_normal.ppm";
          }
          else if(sum >= 26 && sum <= 50) {
              filename = "ultra_bad.ppm";
          }
          else if(sum >= 51) {
              filename = "ultra_sobad.ppm";
          }
      }

    // print image on matrix
    signal(SIGTERM, InterruptHandler);
    signal(SIGINT, InterruptHandler);

    RGBMatrix *matrix = RGBMatrix::CreateFromOptions(matrix_options, runtime_opt);
    if (matrix == NULL)
      return 1;

    ImageVector images = LoadImageAndScaleImage(filename,
                                                matrix->width(),
                                                matrix->height());
        CopyImageToCanvas(images[0], matrix);
        sleep(3);
        matrix->Clear();
        delete matrix;
  }

  /*signal(SIGTERM, InterruptHandler);
  signal(SIGINT, InterruptHandler);

  RGBMatrix *matrix = RGBMatrix::CreateFromOptions(matrix_options, runtime_opt);
  if (matrix == NULL)
    return 1;

  ImageVector images = LoadImageAndScaleImage(filename,
                                              matrix->width(),
                                              matrix->height());
  switch (images.size()) {
  case 0:   // failed to load image.
    break;
  case 1:   // Simple example: one image to show
    CopyImageToCanvas(images[0], matrix);
    while (!interrupt_received) sleep(1000);  // Until Ctrl-C is pressed
    break;
  default:  // More than one image: this is an animation.
    ShowAnimatedImage(images, matrix);
    break;
  }*/
  
  // matrix->Clear();
  // delete matrix;
  fclose(fp);

  return 0;
}
