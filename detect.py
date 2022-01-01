import argparse
import time
from pathlib import Path

import os
import cv2
import torch
import shutil
import torch.backends.cudnn as cudnn
from numpy import random

from deep_sort_pytorch.utils.parser import get_config
from deep_sort_pytorch.deep_sort import DeepSort

from collections import deque

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, non_max_suppression, apply_classifier, scale_coords, xyxy2xywh, \
    strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box, Annotator, colors
from utils.torch_utils import select_device, load_classifier, time_synchronized

#rtsp://admin:SnSlab20121208!@203.250.33.177:554/profile2/media.smp

def detect(save_img=False):
    out, source, weights, deep_sort_weights, view_img, save_txt, imgsz, evaluate = opt.output, opt.source, opt.weights, opt.deep_sort_weights, opt.view_img, opt.save_txt, opt.img_size, opt.evaluate
    webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
        ('rtsp://', 'rtmp://', 'http://'))

    # initialize deepsort
    cfg = get_config()
    cfg.merge_from_file('deep_sort_pytorch/configs/deep_sort.yaml')
    deepsort = DeepSort(cfg.DEEPSORT.REID_CKPT, max_dist=cfg.DEEPSORT.MAX_DIST, min_confidence=cfg.DEEPSORT.MIN_CONFIDENCE,
                        max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE, max_age=cfg.DEEPSORT.MAX_AGE, n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET,
                        use_cuda=True)

    # Directories
    save_dir = Path(increment_path(Path(opt.project) / opt.name, exist_ok=opt.exist_ok))  # increment run
    (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

    # Initialize
    set_logging()
    device = select_device(opt.device)
    half = device.type != 'cpu'  # half precision only supported on CUDA

    if not evaluate:
        if os.path.exists(out):
            pass
            shutil.rmtree(out)  # delete output folder
        os.makedirs(out)  # make new output folder

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    imgsz = check_img_size(imgsz, s=model.stride.max())  # check img_size
    if half:
        model.half()  # to FP16

    # Second-stage classifier
    classify = False
    if classify:
        modelc = load_classifier(name='resnet101', n=2)  # initialize
        modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model']).to(device).eval()

    # Set Dataloader
    vid_path, vid_writer = None, None
    if webcam:
        view_img = True
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz)
    else:
        save_img = True
        dataset = LoadImages(source, img_size=imgsz, auto_size=64)

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names

    # Run inference
    t0 = time.time()
    img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
    _ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once

    pts = [deque(maxlen=5) for _ in range(9999)]

    prev_time = 0
    input_fps = 10
    #for path, img, im0s, vid_cap, i in dataset:
    for path, img, im0s, vid_cap, frame_idx in dataset:
        current_time = time.time() - prev_time
        if current_time > 1./input_fps:
            prev_time = time.time()
            start_time = time.time()
            img = torch.from_numpy(img).to(device)
            img = img.half() if half else img.float()  # uint8 to fp16/32
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)

            # Inference
            t1 = time_synchronized()
            pred = model(img, augment=opt.augment)[0]

            # Apply NMS
            pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, classes=opt.classes, agnostic=opt.agnostic_nms)
            t2 = time_synchronized()

            # Apply Classifier
            if classify:
                pred = apply_classifier(pred, modelc, img, im0s)
            # Process detections
            for i, det in enumerate(pred):  # detections per image
                if webcam:  # batch_size >= 1
                    p, s, im0 = Path(path[i]), '%g: ' % i, im0s[i].copy()
                else:
                    p, s, im0 = Path(path), '', im0s

                save_path = str(save_dir / p.name)
                print(p.name)
                #txt_path = str(save_dir / 'labels' / p.stem) + ('_%g' % dataset.frame if dataset.mode == 'video' else '')
                txt_file_name = source.split('/')[-1].split('.')[0]
                txt_path = str(Path(out)) + '/' + txt_file_name + '.txt'
                s += '%gx%g ' % img.shape[2:]  # print string
                gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh

                annotator = Annotator(im0, line_width=2, pil=not ascii)

                if len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    for c in det[:, -1].unique():
                        n = (det[:, -1] == c).sum()  # detections per class
                        s += '%g %ss, ' % (n, names[int(c)])  # add to string

                    xywhs = xyxy2xywh(det[:, :4]).cpu()
                    confs = det[:, 4].cpu()
                    clss = det[:, 5].cpu()
                    outputs = deepsort.update(xywhs, confs, clss, im0)

                    #Write results
                    # for *xyxy, conf, cls in reversed(det):
                    #     if save_txt:  # Write to file
                    #         xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                    #         line = (cls, *xywh, conf) if opt.save_conf else (cls, *xywh)  # label format
                    #         print(xywh, conf, cls)
                    #         with open(txt_path + '.txt', 'a') as f:
                    #             f.write(('%g ' * len(line)).rstrip() % line + '\n')

                        # if save_img or view_img:  # Add bbox to image
                        #     label = '%s %.2f' % (names[int(clss)], confs)
                        #     plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3)

                    if len(outputs) > 0:
                        identities = outputs[:,4]
                        for j, (output, conf) in enumerate(zip(outputs, confs)):
                            bboxes = output[0:4]
                            id = output[4]
                            cls = output[5]
                            c = int(cls)

                            label = f'{id} {names[c]} {conf:.2f}'
                            annotator.box_label(bboxes, label, color=colors(c, True))
                            #annotator.draw_centroid_log(bboxes, pts, j, identities, color=colors(c, True))

                            # Draw center point & tracking log
                            # x1, y1, x2, y2 = [int(j) for j in bboxes]
                            # id = int(identities[i]) if identities is not None else 0
                            # center = ((round((x1 + x2) / 2), round((y1 + y2) / 2)))
                            # pts[id].append(center)
                            # cv2.circle(im0s, (round((x1 + x2) / 2), round((y1 + y2) / 2)), 1, colors(c, True), 5)
                            #
                            # for f in range(1, len(pts[id])):
                            #     if pts[id][f - 1] is None or pts[id][f] is None:
                            #         continue
                            #     thickness = int(np.sqrt(64 / float(f + 1)) * 2)
                            #     cv2.line(im0s, (pts[id][f - 1]), (pts[id][f]), colors(c, True), thickness)

                            if save_txt:
                                bbox_left = output[0]
                                bbox_top = output[1]
                                bbox_w = output[2] - output[0]
                                bbox_h = output[3] - output[1]
                                print(frame_idx, id, bbox_left, bbox_top, bbox_w, bbox_h)

                                with open(txt_path, 'a') as f:
                                    f.write(('%g ' * 10 + '\n') % (frame_idx, id, bbox_left,
                                                                  bbox_top, bbox_w, bbox_h, -1, -1, -1, -1))

                else:
                    deepsort.increment_ages()

                end_time = time.time()

                # Print time (inference + NMS)
                print('%sDone. (%.3fs)' % (s, t2 - t1))

                # Stream results
                im0 = annotator.result(start_time, end_time)
                if view_img:
                    cv2.imshow("test", im0)
                    if cv2.waitKey(1) == ord('q'):  # q to quit
                        raise StopIteration

                # Save results (image with detections)
                if save_img:
                    if dataset.mode == 'images':
                        cv2.imwrite(save_path, im0)
                    else:
                        if vid_path != save_path:  # new video
                            vid_path = save_path
                            if isinstance(vid_writer, cv2.VideoWriter):
                                vid_writer.release()  # release previous video writer

                            fourcc = 'mp4v'  # output video codec
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*fourcc), fps, (w, h))
                        vid_writer.write(im0)

    if save_txt or save_img:
        print('Results saved to %s' % save_dir)

    print('Done. (%.3fs)' % (time.time() - t0))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='yolor-p6.pt', help='model.pt path(s)')
    parser.add_argument('--deep_sort_weights', type=str, default='deep_sort_pytorch/deep_sort/deep/checkpoint/ckpt.t7', help='ckpt.t7 path')
    parser.add_argument('--source', type=str, default='inference/images', help='source')  # file/folder, 0 for webcam
    parser.add_argument('--output', type=str, default='inference/output', help='output folder')
    parser.add_argument('--img-size', type=int, default=1280, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.4, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='display results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--evaluate', action='store_true', help='augmented inference')
    parser.add_argument('--config_deepsort', type=str, default='deep_sort_pytorch/configs/deep_sort.yaml')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default='runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    opt = parser.parse_args()
    print(opt)

    with torch.no_grad():
        if opt.update:  # update all models (to fix SourceChangeWarning)
            for opt.weights in ['yolor-p6.pt', 'yolor-w6.pt', 'yolor-e6.pt', 'yolor-d6.pt']:
                detect()
                strip_optimizer(opt.weights)
        else:
            detect()
