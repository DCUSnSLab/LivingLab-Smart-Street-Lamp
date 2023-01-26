# LivingLab-Smart-Street-Lamp

### 라즈베리파이에서 실행방법

requirments.txt 를 통해 라이브러리 설치 후

    sudo sh startLamp.sh

터미널에서 입력하면 OTA 실행되며 lampController를 통해 미세먼지 복합 공기질 센서, 일몰 일출 시각 API, 비상버튼, LED matrix 프로세스 실행
gateway/ota/type_definitions.py의 SH_ID와 LAMP_ID 

-----

미세먼지 복합 공기질 센서(gateway/proc_environsensor.py)는 메세지큐를 통해 LED matrix(gateway/rpi-rgb-led-matrix/examples-api-use/text-example)에 데이터 전송 

일몰 일출 시각 API(gateway/proc_api.py)를 통해 가로등 LED 제어

웹소켓을 통해 메세지 "s"를 전송하면 모든 프로세스 종료 후 git clone하고 재실행 (gateway/ota/proc_otacom.py)
