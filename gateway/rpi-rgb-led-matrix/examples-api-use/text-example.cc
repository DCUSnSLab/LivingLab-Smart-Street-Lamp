// -*- mode: c++; c-basic-offset: 2; indent-tabs-mode: nil; -*-
// Small example how write text.
//
// This code is public domain
// (but note, that the led-matrix library this depends on is GPL v2)

#include "led-matrix.h"
#include "graphics.h"
#include "type_definitions.h"

#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>

#define BUFF_SIZE 40

using namespace rgb_matrix;

/* test.cc */
typedef struct {
	long  data_type;
	//int   data_num;
	unsigned char  data_buff[BUFF_SIZE];
} t_data;


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

void strreverse(char* begin, char* end) {
  char aux;
  while(end > begin)
    aux = *end, *end-- = *begin, *begin++ = aux;
}

void itoa(int value, char* str, int base) {
  static char num[] = "0123456789abcdefghijklmnopqrstuvwxyz";
  char* wstr = str;
  int sign;
  div_t res;

  // Validate base
  if (base < 2 || base > 35) {
    *wstr = '\0';
    return;
  }

  // Take care of sign
  if ((sign = value) < 0)
    value = -value;

  // Conversion. Number is reserved.
  do {
    res = div(value, base);
    *wstr++ = num[res.rem];
  } while(value = res.quot);

  if (sign < 0) *wstr++ = '-'; *wstr = '\0';

  // Reverse string
  strreverse(str, wstr - 1);
}


/* start main */
int main(int argc, char *argv[]) {
  
  /* Options */
  int      msqid;
	t_data   data;
	double   dValue1, dValue2;
	char	 new_array[BUFF_SIZE];

  RGBMatrix::Options matrix_options;
  rgb_matrix::RuntimeOptions runtime_opt;
  if (!rgb_matrix::ParseOptionsFromFlags(&argc, &argv,
                                         &matrix_options, &runtime_opt)) {
    return usage(argv[0]);
  }

  Color color(255, 255, 255);
  Color bg_color(0, 0, 0);
  Color flood_color(0, 0, 0);
  Color outline_color(0,0,0);
  bool with_outline = false;

  const char *bdf_font_file = NULL;
  int xm = 0;
  int xs = 0;
  int x_orig = 0;
  int y_orig = 0;
  int letter_spacing = 0;

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

  /*
   * Load font. This needs to be a filename with a bdf bitmap font.
   */
  rgb_matrix::Font font;
  if (!font.LoadFont(bdf_font_file)) {
    fprintf(stderr, "Couldn't load font '%s'\n", bdf_font_file);
    return 1;
  }

  /*
   * If we want an outline around the font, we create a new font with
   * the original font as a template that is just an outline font.
   */
  rgb_matrix::Font *outline_font = NULL;
  if (with_outline) {
    outline_font = font.CreateOutlineFont();
  }

  RGBMatrix *canvas = RGBMatrix::CreateFromOptions(matrix_options, runtime_opt);
  if (canvas == NULL)
    return 1;

  const bool all_extreme_colors = (matrix_options.brightness == 100)
    && FullSaturation(color)
    && FullSaturation(bg_color)
    && FullSaturation(outline_color);
  if (all_extreme_colors)
    canvas->SetPWMBits(1);

  const int x = x_orig;
  int y = y_orig;

  if (isatty(STDIN_FILENO)) {
    // Only give a message if we are interactive. If connected via pipe, be quiet
    printf("Enter lines. Full screen or empty line clears screen.\n"
           "Supports UTF-8. CTRL-D for exit.\n");
  }

  canvas->Fill(flood_color.r, flood_color.g, flood_color.b);

  // write from here
    
  if (outline_font) {
    // The outline font, we need to write with a negative (-2) text-spacing,
    // as we want to have the same letter pitch as the regular text that
    // we then write on top.
    printf("outlinefont\n");
    rgb_matrix::DrawText(canvas, *outline_font,
                        x - 1, y + font.baseline(),
                        outline_color, &bg_color, 0, letter_spacing - 2);
  }

  /* test.cc Code */
  if ( -1 == ( msqid = msgget( (key_t)1234, IPC_CREAT | 0666)))
	{
		perror( "msgget() failed");
		exit( 1);
	}

  while(1) {

    // datatype 0: receive all datatype
    // change datatype to 1 if you want to receive python data

    if(-1 == msgrcv(msqid, &data, sizeof(t_data) - sizeof(long), 0, 0)) {
      perror("msgrcv() failed");
      exit(1);
    }

    printf("*** New message received ***\nRaw data: ");
    for(int i = 0; i < BUFF_SIZE; i++)
      printf("%02X ", data.data_buff[i]);
    printf("\n");

    if(data.data_type == TYPE_STRING)
      printf("Interpreted as string: %15s\n", data.data_buff);
    
    else if(data.data_type == TYPE_TWODOUBLES) {
      memcpy(&dValue1, data.data_buff, sizeof(double));
      memcpy(&dValue2, data.data_buff + sizeof(double), sizeof(double));
      printf("Interpreted as two doubles: %f, %f\n", dValue1, dValue2);
    }

    else if(data.data_type == TYPE_ARRAY) {
      memcpy(new_array, data.data_buff, BUFF_SIZE);
      printf("Interpreted as array: ");
      for(int i = 0; i < BUFF_SIZE; i++)
        printf("%d ", new_array[i]);
      printf("\n");
    }

    else if(data.data_type == TYPE_DOUBLEANDARRAY) {
      memcpy(&dValue1, data.data_buff, sizeof(double));
      memcpy(&dValue2, data.data_buff + sizeof(double), BUFF_SIZE / 2);
      printf("Interpreted as one double and array: %f, ", dValue1);
      for(int i = 0; i < BUFF_SIZE / 2; i++)
        printf("%d ", new_array[i]);
      printf("\n");
    }

    /* print on Matrix */ 

    int CO2_num = (((int) new_array[0]) * 254) + ((int) new_array[4]);
    char CO2[10];
    itoa(CO2_num, CO2, 10);

    rgb_matrix::DrawText(canvas, font, 1, 14,
                      color, outline_font ? NULL : &bg_color, "이산화탄소",
                      letter_spacing);

    rgb_matrix::DrawText(canvas, font, 7, 29,
                      color, outline_font ? NULL : &bg_color, CO2,
                      letter_spacing);

    rgb_matrix::DrawText(canvas, font, 32, 29,
                      color, outline_font ? NULL : &bg_color, "ppm",
                      letter_spacing);

    sleep(3);
    canvas->Clear();


    char HUM[10];
    itoa(new_array[8], HUM, 10);

    rgb_matrix::DrawText(canvas, font, 20, 14,
                      color, outline_font ? NULL : &bg_color, "습도",
                      letter_spacing);

    rgb_matrix::DrawText(canvas, font, 20, 29,
                      color, outline_font ? NULL : &bg_color, HUM,
                      letter_spacing);

    rgb_matrix::DrawText(canvas, font, 36, 29,
                      color, outline_font ? NULL : &bg_color, "%",
                      letter_spacing);

    sleep(3);
    canvas->Clear();


    char TEMP[10];
    itoa(new_array[12], TEMP, 10);
    if(new_array[12] < 0) 
      xs = 15;
    else if(new_array[12] >= 0 && new_array[12] <= 9) {
      xs = 20;
      if(new_array[12] == 1) 
        xs = 25;
    }
    else 
      xs = 20;
      

    rgb_matrix::DrawText(canvas, font, 21, 14,
                      color, outline_font ? NULL : &bg_color, "기온",
                      letter_spacing);

    rgb_matrix::DrawText(canvas, font, xs, 29,
                      color, outline_font ? NULL : &bg_color, TEMP,
                      letter_spacing);

    rgb_matrix::DrawText(canvas, font, 36, 29,
                      color, outline_font ? NULL : &bg_color, "도",
                      letter_spacing);

    sleep(3);
    canvas->Clear();


    int FINE_num = (int) new_array[16];
    char FINE[10];
    itoa(new_array[16], FINE, 10);

    rgb_matrix::DrawText(canvas, font, 7, 14,
                      color, outline_font ? NULL : &bg_color, "미세먼지",
                      letter_spacing);

    if(FINE_num >= 0 && FINE_num <= 30) {
              color.r = 0;
              color.g = 0;
              color.b = 255;
    }
    else if(FINE_num >= 31 && FINE_num <= 50) {
              color.r = 0;
              color.g = 255;
              color.b = 0;
    }
    else if(FINE_num >= 51 && FINE_num <= 100) {
              color.r = 255;
              color.g = 255;
              color.b = 0;
    }
    else if(FINE_num >= 101) {
              color.r = 255;
              color.g = 0;
              color.b = 0;
    }

    if(FINE_num >= 0 && FINE_num <= 9) {
      if(FINE_num == 1)
        xm = 30;
      else
        xm = 28;
    }
    else if(FINE_num >= 10 && FINE_num <= 99)
      xm = 25;

    rgb_matrix::DrawText(canvas, font, xm, 29,
                      color, outline_font ? NULL : &bg_color, FINE,
                      letter_spacing);

    sleep(3);
    canvas->Clear();

    rgb_matrix::DrawText(canvas, font, 7, 14,
                      color, outline_font ? NULL : &bg_color, "미세먼지",
                      letter_spacing);

    if(FINE_num >= 0 && FINE_num <= 30) {
              xs = 20;
              rgb_matrix::DrawText(canvas, font, xs, 29,
                      color, outline_font ? NULL : &bg_color, "좋음",
                      letter_spacing);
    }
    else if(FINE_num >= 31 && FINE_num <= 50) {
              xs = 20;
              rgb_matrix::DrawText(canvas, font, xs, 29,
                      color, outline_font ? NULL : &bg_color, "보통",
                      letter_spacing);
    }
    else if(FINE_num >= 51 && FINE_num <= 100) {
              xs = 20;
              rgb_matrix::DrawText(canvas, font, xs, 29,
                      color, outline_font ? NULL : &bg_color, "나쁨",
                      letter_spacing);
    }
    else if(FINE_num >= 101) {
              xs = 4;
              rgb_matrix::DrawText(canvas, font, xs, 29,
                      color, outline_font ? NULL : &bg_color, "매우 나쁨",
                      letter_spacing);
    }

    sleep(3);
    canvas->Clear();


    int ULTRA_num = (int) new_array[20];
    char ULTRA[10];
    itoa(new_array[20], ULTRA, 10);

    color.r = 255;
    color.g = 255;
    color.b = 255;

    rgb_matrix::DrawText(canvas, font, 1, 14,
                      color, outline_font ? NULL : &bg_color, "초미세먼지",
                      letter_spacing);

    if(ULTRA_num >= 0 && ULTRA_num <= 15) {
              color.r = 0;
              color.g = 0;
              color.b = 255;
    }
    else if(ULTRA_num >= 16 && ULTRA_num <= 25) {
              color.r = 0;
              color.g = 255;
              color.b = 0;
    }
    else if(ULTRA_num >= 26 && ULTRA_num <= 50) {
              color.r = 255;
              color.g = 255;
              color.b = 0;
    }
    else if(ULTRA_num >= 51) {
              color.r = 255;
              color.g = 0;
              color.b = 0;
    }

    if(ULTRA_num >= 0 && ULTRA_num <= 9) {
      if(ULTRA_num == 1)
        xm = 30;
      else
        xm = 28;
    }
    else if(ULTRA_num >= 10 && ULTRA_num <= 99)
      xm = 25;
    
    rgb_matrix::DrawText(canvas, font, xm, 29,
                      color, outline_font ? NULL : &bg_color, ULTRA,
                      letter_spacing);
    
    sleep(3);
    canvas->Clear();

    rgb_matrix::DrawText(canvas, font, 1, 14,
                      color, outline_font ? NULL : &bg_color, "초미세먼지",
                      letter_spacing);

    if(ULTRA_num >= 0 && ULTRA_num <= 15) {
              xs = 20;
              rgb_matrix::DrawText(canvas, font, xs, 29,
                      color, outline_font ? NULL : &bg_color, "좋음",
                      letter_spacing);
    }
    else if(ULTRA_num >= 16 && ULTRA_num <= 25) {
              xs = 20;
              rgb_matrix::DrawText(canvas, font, xs, 29,
                      color, outline_font ? NULL : &bg_color, "보통",
                      letter_spacing);
    }
    else if(ULTRA_num >= 26 && ULTRA_num <= 50) {
              xs = 20;
              rgb_matrix::DrawText(canvas, font, xs, 29,
                      color, outline_font ? NULL : &bg_color, "나쁨",
                      letter_spacing);
    }
    else if(ULTRA_num >= 51) {
              xs = 4;
              rgb_matrix::DrawText(canvas, font, xs, 29,
                      color, outline_font ? NULL : &bg_color, "매우 나쁨",
                      letter_spacing);
    }

    sleep(3);
    canvas->Clear();


    /* print clock */

    color.r = 255;
    color.g = 255;
    color.b = 255;

    time_t timer = time(NULL);
    char timeNow[10] = {'0', '0', ':', '0', '0', ' ', ' ', ' ', ' ', ' '};
    struct tm* t;
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

    rgb_matrix::DrawText(canvas, font, 17, 21,
                          color, outline_font ? NULL : &bg_color, timeNow,
                          letter_spacing);
                        
    sleep(3);
    canvas->Clear();

  }

  delete canvas;

  return 0;
}
