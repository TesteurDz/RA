import Flutter
import UIKit

@main
<<<<<<< HEAD
@objc class AppDelegate: FlutterAppDelegate, FlutterImplicitEngineDelegate {
=======
@objc class AppDelegate: FlutterAppDelegate {
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
<<<<<<< HEAD
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }

  func didInitializeImplicitFlutterEngine(_ engineBridge: FlutterImplicitEngineBridge) {
    GeneratedPluginRegistrant.register(with: engineBridge.pluginRegistry)
  }
=======
    GeneratedPluginRegistrant.register(with: self)
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
}
