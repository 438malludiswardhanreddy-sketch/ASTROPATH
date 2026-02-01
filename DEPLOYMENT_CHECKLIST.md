# ✅ ASTROPATH Deployment Checklist

Use this checklist to ensure everything is ready before deployment.

---

## 🚀 Pre-Deployment Checklist

### Phase 1: Development Environment (Day 1)

- [ ] **Downloaded Project Files**
  - [ ] All Python files in src/
  - [ ] config.py exists
  - [ ] main.py exists
  - [ ] requirements.txt exists

- [ ] **Python Environment**
  - [ ] Python 3.8+ installed
  - [ ] Virtual environment created
  - [ ] venv activated
  - [ ] pip install -r requirements.txt completed

- [ ] **Model Files**
  - [ ] YOLOv4-tiny.weights downloaded (196 MB)
  - [ ] Placed in models/ directory
  - [ ] yolov4-tiny.cfg verified in models/
  - [ ] obj.names created with "pothole"

- [ ] **Documentation Read**
  - [ ] PROJECT_OVERVIEW.md reviewed
  - [ ] README.md read
  - [ ] SETUP_GUIDE.md followed
  - [ ] QUICK_REFERENCE.md bookmarked

---

### Phase 2: Basic Testing (Day 2)

- [ ] **Configuration**
  - [ ] config.py reviewed
  - [ ] CAMERA_SOURCE set correctly
  - [ ] API_URL updated (or set to disabled)
  - [ ] DEBUG_MODE enabled for testing

- [ ] **Functionality Tests**
  - [ ] python main.py runs without errors
  - [ ] Menu displays correctly
  - [ ] Option 1: Train works (with training data)
  - [ ] Option 2: Detection runs
  - [ ] Option 3: Web form starts
  - [ ] Option 4: API test completes

- [ ] **Basic Detection**
  - [ ] Webcam opens successfully
  - [ ] Frames display in window
  - [ ] Press 'q' exits cleanly
  - [ ] Images saved to detections/
  - [ ] Log file created

- [ ] **Directory Structure**
  - [ ] models/ has necessary files
  - [ ] data/ directory exists
  - [ ] detections/ created after first run
  - [ ] uploads/ created after citizen upload
  - [ ] No permission errors

---

### Phase 3: Training (If Applicable) (Days 3-5)

- [ ] **Training Data Preparation**
  - [ ] pothole images collected (50+ or 100+ ideally)
  - [ ] Organized in data/training_images/pothole/
  - [ ] Plain road images collected (50+ or 100+ ideally)
  - [ ] Organized in data/training_images/plain/
  - [ ] File formats verified (JPG/PNG)
  - [ ] No corrupted images

- [ ] **Training Execution**
  - [ ] python main.py → Select 1
  - [ ] Training starts without errors
  - [ ] Loss decreases over epochs
  - [ ] Validation accuracy improves
  - [ ] Model saved: models/custom_classifier.h5
  - [ ] Training completes successfully

- [ ] **Model Validation**
  - [ ] Trained model loads without errors
  - [ ] Predictions run without crashes
  - [ ] Output shapes correct
  - [ ] Performance acceptable (>80% accuracy)

---

### Phase 4: Advanced Detection (Days 6-7)

- [ ] **Video File Testing**
  - [ ] Test video placed in data/
  - [ ] CAMERA_SOURCE points to video
  - [ ] Detection runs on video
  - [ ] Output video generated
  - [ ] Bounding boxes annotated correctly
  - [ ] Severity levels displayed

- [ ] **Severity Estimation**
  - [ ] Low severity potholes marked green
  - [ ] Medium severity marked orange
  - [ ] High severity marked red
  - [ ] Colors visible in output
  - [ ] Thresholds appropriate

- [ ] **Logging & Monitoring**
  - [ ] astropath.log created
  - [ ] Logs contain detection info
  - [ ] FPS counter displays
  - [ ] Detection counter increments
  - [ ] No verbose spam in logs

---

### Phase 5: Integration Ready (Week 2)

- [ ] **API Configuration**
  - [ ] API_URL configured correctly
  - [ ] ENABLE_CLOUD_UPLOAD set appropriately
  - [ ] api_client.py tested
  - [ ] Mock API call succeeds
  - [ ] Error handling works

- [ ] **Citizen Web App**
  - [ ] python src/citizen_upload.py runs
  - [ ] http://localhost:5000 loads
  - [ ] Form displays correctly
  - [ ] File upload works
  - [ ] Location button functional
  - [ ] Submit sends data

- [ ] **Data Handling**
  - [ ] Detection images saved with timestamps
  - [ ] JSON payloads well-formatted
  - [ ] Citizen uploads organized
  - [ ] File permissions correct
  - [ ] Cleanup script working (if created)

---

### Phase 6: Raspberry Pi Deployment (Week 2-3)

- [ ] **Environment Setup**
  - [ ] Raspberry Pi OS installed
  - [ ] SSH access configured
  - [ ] Network connectivity verified
  - [ ] Python 3.8+ installed on Pi
  - [ ] Virtual environment created

- [ ] **Dependency Installation**
  - [ ] pip install -r requirements.txt on Pi
  - [ ] TensorFlow installed (or TFLite)
  - [ ] OpenCV installed
  - [ ] Flask installed
  - [ ] All imports successful

- [ ] **Configuration for Pi**
  - [ ] PI_OPTIMIZE = True in config.py
  - [ ] IMG_SIZE_YOLO reduced (320 or 416)
  - [ ] DETECTION_FRAME_SKIP optimized
  - [ ] CAMERA_SOURCE set to Pi camera (0)
  - [ ] API_URL configured

- [ ] **Pi Testing**
  - [ ] main.py runs on Pi
  - [ ] Detection works on Pi
  - [ ] FPS acceptable (5-10+)
  - [ ] Memory usage monitored
  - [ ] Heat dissipation adequate
  - [ ] 24-hour test successful

- [ ] **Optional: Hardware Integration**
  - [ ] GPS module tested (if available)
  - [ ] Ultrasonic sensor calibrated (if used)
  - [ ] Camera stream working
  - [ ] Power management setup
  - [ ] Auto-restart on boot configured

---

### Phase 7: Cloud Integration (Week 3-4)

- [ ] **Backend Preparation**
  - [ ] Cloud service account created
  - [ ] Database configured
  - [ ] API endpoints built
  - [ ] Authentication tested
  - [ ] Storage buckets ready

- [ ] **API Testing**
  - [ ] /api/report endpoint works
  - [ ] /api/heatmap returns data
  - [ ] /api/status returns 200
  - [ ] Error handling tested
  - [ ] Rate limiting configured

- [ ] **End-to-End Testing**
  - [ ] Detection runs on edge device
  - [ ] Auto-uploads to cloud
  - [ ] Data appears in dashboard
  - [ ] No data loss
  - [ ] Latency acceptable (<2 sec)

- [ ] **Monitoring & Alerts**
  - [ ] Logging configured
  - [ ] Error alerts set up
  - [ ] Performance metrics tracked
  - [ ] Uptime monitoring enabled

---

### Phase 8: Production Readiness (Week 4+)

- [ ] **Security**
  - [ ] API authentication enabled
  - [ ] Data encryption configured
  - [ ] Credentials not in code
  - [ ] Environment variables used
  - [ ] No hardcoded secrets

- [ ] **Performance**
  - [ ] Load testing completed
  - [ ] Latency within SLA
  - [ ] Memory usage optimized
  - [ ] CPU usage monitored
  - [ ] Bottlenecks identified

- [ ] **Reliability**
  - [ ] Error recovery tested
  - [ ] Fallback mechanisms work
  - [ ] Data backup configured
  - [ ] Disaster recovery plan
  - [ ] Rollback procedure documented

- [ ] **Documentation**
  - [ ] Deployment guide written
  - [ ] Troubleshooting guide updated
  - [ ] API documentation complete
  - [ ] Configuration guide finalized
  - [ ] Operations manual created

- [ ] **Scaling**
  - [ ] Multiple instances tested
  - [ ] Load balancing configured
  - [ ] Database scaling ready
  - [ ] Storage scaling plan
  - [ ] Cost optimization done

---

## 🎯 Quick Verification (5-Minute Check)

Before each deployment, verify:

```
✅ Python installed?           python --version
✅ Dependencies?               pip list | grep tensorflow
✅ Model files?                ls models/
✅ Code runs?                  python main.py
✅ Detections saved?           ls detections/
✅ No errors in logs?          tail astropath.log
✅ API reachable?              curl API_URL
✅ Storage available?          df -h
✅ Network connected?          ping google.com
✅ Time synchronized?          date
```

---

## 🚨 Critical Issues (Stop Deployment If Any!)

- [ ] YOLOv4-tiny.weights missing
- [ ] Python dependencies not installed
- [ ] Model initialization fails
- [ ] Camera/video not accessible
- [ ] File permissions errors
- [ ] Out of disk space (<1 GB free)
- [ ] Memory insufficient (<512 MB free)
- [ ] Network disconnected
- [ ] API unreachable
- [ ] GPU CUDA errors (not critical)

---

## ✨ Optional Enhancements (Pre-Launch)

- [ ] Custom training data prepared
- [ ] Web dashboard styled
- [ ] Mobile app ready
- [ ] Drone integration tested
- [ ] Multi-class detection working
- [ ] Real-time analytics enabled
- [ ] SMS/Email notifications set
- [ ] Repair crew portal built
- [ ] Citizen app deployed
- [ ] Marketing materials ready

---

## 📋 Pre-Launch Verification

**48 Hours Before Launch:**

- [ ] All checklists above completed
- [ ] Stress testing finished
- [ ] Documentation reviewed
- [ ] Team trained
- [ ] Support contact information updated
- [ ] Backup systems verified
- [ ] Monitoring dashboards live
- [ ] Alert thresholds set
- [ ] Incident response plan ready
- [ ] Launch communication prepared

**24 Hours Before Launch:**

- [ ] Final system tests passed
- [ ] Database backup created
- [ ] Configuration backed up
- [ ] Rollback procedures tested
- [ ] Team briefing completed
- [ ] Launch timeline confirmed
- [ ] Contingency plans ready

**Launch Day:**

- [ ] System online
- [ ] Initial monitoring active
- [ ] Team standby ready
- [ ] Support channels open
- [ ] Customer communication ready

---

## 🎉 Post-Launch Checklist

**First 24 Hours:**

- [ ] System stable
- [ ] Detections working
- [ ] Cloud sync successful
- [ ] No critical errors
- [ ] User reports accepted
- [ ] Team notified of any issues

**First Week:**

- [ ] All features validated
- [ ] Performance metrics tracked
- [ ] User feedback collected
- [ ] Bugs logged and prioritized
- [ ] Optimization identified

**First Month:**

- [ ] System fully stabilized
- [ ] Analytics reviewed
- [ ] Improvements implemented
- [ ] Scaling plan finalized
- [ ] Documentation updated

---

## 📞 Emergency Contacts

| Role | Contact | Status |
|------|---------|--------|
| Technical Lead | | |
| Operations Manager | | |
| System Administrator | | |
| Cloud Provider Support | | |
| API Provider Support | | |

---

## 📝 Sign-Off

- [ ] **Developer**: _________________ Date: _______
- [ ] **QA**: _________________ Date: _______
- [ ] **DevOps**: _________________ Date: _______
- [ ] **Manager**: _________________ Date: _______

---

## 🎯 Next Steps

After completing this checklist:

1. Review completed items
2. Address any failed items
3. Get sign-offs from team
4. Deploy to production
5. Monitor closely
6. Collect feedback
7. Iterate and improve

---

**ASTROPATH Deployment Checklist**  
**Version:** 1.0  
**Last Updated:** January 31, 2026  
**Status:** Ready for Use ✅

*Use this checklist for every deployment to ensure success!* 🚀
