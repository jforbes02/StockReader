//
//  ClassifyLogos.swift
//  stockreaderapp
//
//  Created by Justin Forbes on 11/22/26.
//

import CoreML
import Vision

final class ClassifyLogos {
    private let request : VNCoreMLRequest
    
    init() throws {
        let coreML = try mag7(configuration: MLModelConfiguration()).model
        let vnModel = try VNCoreMLModel(for: coreML)
        
        
        request = VNCoreMLRequest(model: vnModel)
        request.imageCropAndScaleOption = .centerCrop
    }
    
    func findLogo(_ pixelBuffer: CVPixelBuffer) -> (label: String, confidence: Float, boundingBox: CGRect)? {
        
        let saliencyRequest = VNGenerateObjectnessBasedSaliencyImageRequest()

        let handler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer, orientation: .right)
        try? handler.perform([request])
        guard let top = (request.results as? [VNClassificationObservation])?.first,
                   top.confidence > 0.75 else { return nil }
        
        let boundingBox = (saliencyRequest.results?.first as? VNSaliencyImageObservation)?.salientObjects?.first?.boundingBox ?? .zero
        
        return (top.identifier, top.confidence, boundingBox)
    }
}
