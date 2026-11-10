// Copyright (C) 2018-2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0
//

#include <ros/ros.h>
#include <sensor_msgs/Image.h>
#include <cv_bridge/cv_bridge.h>

#include <iostream>
#include <limits>

#include <gflags/gflags.h>
#include <utils/images_capture.h>

#include "detectors.hpp"
#include "face.hpp"
#include "visualizer.hpp"

class InteractiveFaceROS
{
public:
    InteractiveFaceROS();

private:
    PerformanceMetrics metrics;

    std::string models_path = "/home/mustar/ekd_catkin_ws/src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_openvino/models/";
    std::string FLAGS_m   = models_path + "face-detection-adas-0001.xml";
    std::string FLAGS_mag = models_path + "age-gender-recognition-retail-0013.xml";
    std::string FLAGS_mhp = models_path + "head-pose-estimation-adas-0001.xml";
    std::string FLAGS_mem = models_path + "emotions-recognition-retail-0003.xml";
    std::string FLAGS_mlm = models_path + "facial-landmarks-35-adas-0002.xml";
    std::string FLAGS_mam = models_path + "anti-spoof-mn3.xml";
    std::string FLAGS_d = "CPU";
    bool FLAGS_r = false;
    bool FLAGS_smooth = true;
    bool FLAGS_show = true;
    bool FLAGS_show_emotion_bar = false;
    double FLAGS_t = 0.5;
    double FLAGS_bb_enlarge_coef = 1.2;
    double FLAGS_dx_coef = 1;
    double FLAGS_dy_coef = 1;
    double FLAGS_fps = -std::numeric_limits<double>::infinity();

    ov::Core core;

    FaceDetection faceDetector;
    AgeGenderDetection ageGenderDetector;
    HeadPoseDetection headPoseDetector;
    EmotionsDetection emotionsDetector;
    FacialLandmarksDetection facialLandmarksDetector;
    AntispoofingClassifier antispoofingClassifier;

    Timer timer;
    std::ostringstream out;
    size_t framesCounter = 0;
    double msrate = 1000.0 / FLAGS_fps;
    std::list<Face::Ptr> faces;
    size_t id = 0;

    ros::NodeHandle nh_;
    ros::Subscriber sub_;

    void init();
    void callback(const sensor_msgs::ImageConstPtr& msg);
};

InteractiveFaceROS::InteractiveFaceROS() {
    init();
}

void InteractiveFaceROS::init() {
    faceDetector.init(FLAGS_m, FLAGS_t, FLAGS_r, static_cast<float>(FLAGS_bb_enlarge_coef),
                      static_cast<float>(FLAGS_dx_coef), static_cast<float>(FLAGS_dy_coef));
    ageGenderDetector.init(FLAGS_mag, FLAGS_r);
    headPoseDetector.init(FLAGS_mhp, FLAGS_r);
    emotionsDetector.init(FLAGS_mem, FLAGS_r);
    facialLandmarksDetector.init(FLAGS_mlm, FLAGS_r);
    antispoofingClassifier.init(FLAGS_mam, FLAGS_r);

    Load(faceDetector).into(core, FLAGS_d);
    Load(ageGenderDetector).into(core, FLAGS_d);
    Load(headPoseDetector).into(core, FLAGS_d);
    Load(emotionsDetector).into(core, FLAGS_d);
    Load(facialLandmarksDetector).into(core, FLAGS_d);
    Load(antispoofingClassifier).into(core, FLAGS_d);
    sub_ = nh_.subscribe("/camera/color/image_raw", 1, &InteractiveFaceROS::callback, this);
}

void InteractiveFaceROS::callback(const sensor_msgs::ImageConstPtr& msg) {
    auto startTime = std::chrono::steady_clock::now();
    cv::Mat frame = cv_bridge::toCvCopy(msg, "bgr8")->image;

    Visualizer visualizer{frame.size()};
    if (FLAGS_show_emotion_bar && emotionsDetector.enabled()) {
        visualizer.enableEmotionBar(emotionsDetector.emotionsVec);
    }

    // Detecting all faces on the first frame and reading the next one
    faceDetector.submitRequest(frame);

    if (frame.data) {
        timer.start("total");
        framesCounter++;

        std::vector<FaceDetection::Result> detection_results = faceDetector.fetchResults();

        // Filling inputs of face analytics networks
        for (auto &&face : detection_results) {
            cv::Rect clippedRect = face.location & cv::Rect({0, 0}, frame.size());
            const cv::Mat& crop = frame(clippedRect);
            ageGenderDetector.enqueue(crop);
            headPoseDetector.enqueue(crop);
            emotionsDetector.enqueue(crop);
            facialLandmarksDetector.enqueue(crop);
            antispoofingClassifier.enqueue(crop);
        }

        // Running Age/Gender Recognition, Head Pose Estimation, Emotions Recognition, Facial Landmarks Estimation and Antispoofing Classifier networks simultaneously
        ageGenderDetector.submitRequest();
        headPoseDetector.submitRequest();
        emotionsDetector.submitRequest();
        facialLandmarksDetector.submitRequest();
        antispoofingClassifier.submitRequest();

        //  Postprocessing
        std::list<Face::Ptr> prev_faces;

        if (!FLAGS_smooth) {
            prev_faces.insert(prev_faces.begin(), faces.begin(), faces.end());
        }

        faces.clear();

        // For every detected face
        for (size_t i = 0; i < detection_results.size(); i++) {
            auto& result = detection_results[i];
            cv::Rect rect = result.location & cv::Rect({0, 0}, frame.size());

            Face::Ptr face;
            if (FLAGS_smooth) {
                face = matchFace(rect, prev_faces);
                float intensity_mean = calcMean(frame(rect));

                if ((face == nullptr) ||
                    ((std::abs(intensity_mean - face->_intensity_mean) / face->_intensity_mean) > 0.07f)) {
                    face = std::make_shared<Face>(id++, rect);
                } else {
                    prev_faces.remove(face);
                }

                face->_intensity_mean = intensity_mean;
                face->_location = rect;
            } else {
                face = std::make_shared<Face>(id++, rect);
            }

            face->ageGenderEnable(ageGenderDetector.enabled());
            if (face->isAgeGenderEnabled()) {
                AgeGenderDetection::Result ageGenderResult = ageGenderDetector[i];
                face->updateGender(ageGenderResult.maleProb);
                face->updateAge(ageGenderResult.age);
            }

            face->emotionsEnable(emotionsDetector.enabled());
            if (face->isEmotionsEnabled()) {
                face->updateEmotions(emotionsDetector[i]);
            }

            face->headPoseEnable(headPoseDetector.enabled());
            if (face->isHeadPoseEnabled()) {
                face->updateHeadPose(headPoseDetector[i]);
            }

            face->landmarksEnable(facialLandmarksDetector.enabled());
            if (face->isLandmarksEnabled()) {
                face->updateLandmarks(facialLandmarksDetector[i]);
            }

            face->antispoofingEnable(antispoofingClassifier.enabled());
            if (face->isAntispoofingEnabled()) {
                face->updateRealFaceConfidence(antispoofingClassifier[i]);
            }

            faces.push_back(face);
        }

        // drawing faces
        visualizer.draw(frame, faces);

        metrics.update(startTime, frame, { 10, 22 }, cv::FONT_HERSHEY_COMPLEX, 0.65);

        timer.finish("total");

        int delay = std::max(1, static_cast<int>(msrate - timer["total"].getLastCallDuration()));
        if (FLAGS_show) {
            cv::imshow("Interactive Face Detection", frame);
            int key = cv::waitKey(delay);
            if ('P' == key || 'p' == key || '0' == key || ' ' == key) {
                key = cv::waitKey(0);
            }
        }
    }

    slog::info << "Metrics report:" << slog::endl;
    metrics.logTotal();
}

int main(int argc, char *argv[]){
    ros::init(argc, argv, "interactive_face_ros");
    InteractiveFaceROS node;
    ros::spin();
    return 0;
}
