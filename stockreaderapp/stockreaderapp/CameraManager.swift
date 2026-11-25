//
//  CameraManager.swift
//  stockreaderapp
//
//  Created by Justin Forbes on 10/6/26.
//

import AVFoundation
import SwiftUI
import Combine


class CameraManager: NSObject, ObservableObject, AVCaptureFileOutputRecordingDelegate, AVCaptureVideoDataOutputSampleBufferDelegate{
    
    func fileOutput(_ output: AVCaptureFileOutput, didFinishRecordingTo outputFileURL: URL, from connections: [AVCaptureConnection], error: (any Error)?) {
        if let error = error {
            print("Video recording error \(error.localizedDescription)")
            return
        }
        
        DispatchQueue.main.async{
            [weak self] in
            self?.recordedVideoURL = outputFileURL
        }
    }
    
    @Published var isCameraRunning: Bool = false
    @Published var authStatus: AVAuthorizationStatus = .notDetermined //camera perms
    @Published var isRecording = false
    @Published var recordedVideoURL: URL?
    private var outputURL: URL?
    private var isConfigured = false
    
    // AvFoundation Comps
    let session = AVCaptureSession()
    private let videoOutput = AVCaptureMovieFileOutput()
    private let videoDataOutput = AVCaptureVideoDataOutput() //This handles the ML model
    
    private var currentInput: AVCaptureDeviceInput?
    
    
    private let sessionQueue = DispatchQueue(label: "com.stockreader.sessionQueue") //makes sure the camera doesn't lock the UI thread
    
    // ML Comps
    private let classifier = try? ClassifyLogos()
    @Published var detectedCompany: String?
    @Published var detectedBoundingBox: CGRect?
    
    
    override init() {
        super.init()
    }
    
    func checkAuth(){
        switch AVCaptureDevice.authorizationStatus(for: .video){
            
            // authorized starts session setup
        case .authorized:
            authStatus = .authorized
            setupSession()
            
            // wait for user response
        case .notDetermined:
            authStatus = .notDetermined
            AVCaptureDevice.requestAccess(for: .video){[weak self] granted in
                DispatchQueue.main.async {
                    self?.authStatus = granted ? .authorized : .denied
                    if granted {
                        self?.setupSession()
                    }
                }
                
            }
            // if restricted or denied full stop deny
        case .restricted, .denied:
            authStatus = .denied
            
        @unknown default:
            authStatus = .denied
            
        }
    }
    
    func setupSession(){
        sessionQueue.async {
            [weak self] in
            guard let self = self else { return }
            
            
            //
            if self.isConfigured {
                if !self.session.isRunning {self.session.startRunning()}
                return
            }
            self.isConfigured = true
            
            // sets session protect
            self.session.beginConfiguration()
            self.session.sessionPreset = .high
            
            // cam input
            guard let camera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back), let input = try? AVCaptureDeviceInput(device: camera) else {
                print("Failed access to camera")
                self.session.commitConfiguration()
                return
            }
            
            //ML pipeline hook

            
            if self.session.canAddInput(input){
                self.session.addInput(input)
                self.currentInput = input
            }
            
            
            if self.session.canAddOutput(self.videoOutput){
                self.session.addOutput(self.videoOutput)
            }
            if self.session.canAddOutput(self.videoDataOutput){
                self.session.addOutput(self.videoDataOutput)
                self.videoDataOutput.setSampleBufferDelegate(self, queue: sessionQueue)
                
            }
                
            
            self.session.commitConfiguration()
            
            //session start
            self.session.startRunning()
            
            DispatchQueue.main.async{
                self.isCameraRunning = self.session.isRunning
            }
        }
    }
    
    
    func startRecording(){
        sessionQueue.async {
            [weak self] in
            guard let self = self else { return }
            
            let tempURL = FileManager.default.temporaryDirectory
                .appendingPathComponent(UUID().uuidString)
                .appendingPathExtension("mov")
            
            self.outputURL = tempURL
            
            // start actual recording
            self.videoOutput.startRecording(to: tempURL, recordingDelegate: self)
            
            DispatchQueue.main.async{
                self.isRecording = true
            }
        }
    }
    
    func stopRecording(){
        sessionQueue.async {
            [weak self] in
            self?.videoOutput.stopRecording()
            
            DispatchQueue.main.async {
                self?.isRecording = false
            }
        }
    }
    
    
    //the capture output runs the model 60 times per frame which is a bit odd to me
    //not sure if it needs to run that much
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from
                       connection: AVCaptureConnection) {
        
        
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else {return}
        
        //Changed result so that the stock disappears when not detected
        let result = classifier?.findLogo(pixelBuffer)
        
        
        DispatchQueue.main.async {
            self.detectedCompany = result?.label
            self.detectedBoundingBox = result?.boundingBox
        }
    }
}

