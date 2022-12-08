# LivingLab-Smart-Street-Lamp
Smart Street Lamp

#### 라즈베리파이에서 실행방법

requirments.txt 를 통해 라이브러리 설치 후

    sudo sh startLamp.sh

실행하면 OTA와 미세먼지 복합 공기질 센서, 일몰 일출 시각 API, 비상버튼, LED matrix 프로세스 실행

-----

미세먼지 복합 공기질 센서는 메세지큐를 통해 LED matrix에 데이터 전송 

일몰 일출 시각 API를 통해 가로등 LED 제어

코드 수정 사항이 생기면 웹소켓을 통해 메세지 전송하여 모든 프로세스 종료 후 git clone하고 
재실행 (gateway/ota/proc_otacom.py)
