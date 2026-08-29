import os
import json
import subprocess

src_icon = "images/FavIcon.png"
src_logo = "images/SpiceMartLogo.png"
xcassets_dir = "ios/SpiceMart/Resources/Assets.xcassets"
appicon_dir = os.path.join(xcassets_dir, "AppIcon.appiconset")
logo_dir = os.path.join(xcassets_dir, "SpiceMartLogo.imageset")

os.makedirs(appicon_dir, exist_ok=True)
os.makedirs(logo_dir, exist_ok=True)

# 1. Generate AppIcon variants
icon_specs = [
    # Universal / App Store
    {"filename": "AppIcon-1024.png", "idiom": "universal", "platform": "ios", "size": "1024x1024", "px": 1024},
    
    # iPhone Icons
    {"filename": "AppIcon-20@2x.png", "idiom": "iphone", "size": "20x20", "scale": "2x", "px": 40},
    {"filename": "AppIcon-20@3x.png", "idiom": "iphone", "size": "20x20", "scale": "3x", "px": 60},
    {"filename": "AppIcon-29@2x.png", "idiom": "iphone", "size": "29x29", "scale": "2x", "px": 58},
    {"filename": "AppIcon-29@3x.png", "idiom": "iphone", "size": "29x29", "scale": "3x", "px": 87},
    {"filename": "AppIcon-40@2x.png", "idiom": "iphone", "size": "40x40", "scale": "2x", "px": 80},
    {"filename": "AppIcon-40@3x.png", "idiom": "iphone", "size": "40x40", "scale": "3x", "px": 120},
    {"filename": "AppIcon-60@2x.png", "idiom": "iphone", "size": "60x60", "scale": "2x", "px": 120},
    {"filename": "AppIcon-60@3x.png", "idiom": "iphone", "size": "60x60", "scale": "3x", "px": 180},
    
    # iPad Icons
    {"filename": "AppIcon-20@1x.png", "idiom": "ipad", "size": "20x20", "scale": "1x", "px": 20},
    {"filename": "AppIcon-20@2x-ipad.png", "idiom": "ipad", "size": "20x20", "scale": "2x", "px": 40},
    {"filename": "AppIcon-29@1x.png", "idiom": "ipad", "size": "29x29", "scale": "1x", "px": 29},
    {"filename": "AppIcon-29@2x-ipad.png", "idiom": "ipad", "size": "29x29", "scale": "2x", "px": 58},
    {"filename": "AppIcon-40@1x.png", "idiom": "ipad", "size": "40x40", "scale": "1x", "px": 40},
    {"filename": "AppIcon-40@2x-ipad.png", "idiom": "ipad", "size": "40x40", "scale": "2x", "px": 80},
    {"filename": "AppIcon-76@1x.png", "idiom": "ipad", "size": "76x76", "scale": "1x", "px": 76},
    {"filename": "AppIcon-76@2x.png", "idiom": "ipad", "size": "76x76", "scale": "2x", "px": 152},
    {"filename": "AppIcon-83.5@2x.png", "idiom": "ipad", "size": "83.5x83.5", "scale": "2x", "px": 167},
    
    # iOS Marketing App Store
    {"filename": "AppIcon-1024-ios-marketing.png", "idiom": "ios-marketing", "size": "1024x1024", "scale": "1x", "px": 1024}
]

images_json = []

print("Generating iOS AppIcon files...")
for spec in icon_specs:
    fn = spec["filename"]
    px = spec["px"]
    out_path = os.path.join(appicon_dir, fn)
    subprocess.run(["sips", "-z", str(px), str(px), src_icon, "--out", out_path], check=True)
    
    item = {
        "filename": fn,
        "idiom": spec["idiom"],
        "size": spec["size"]
    }
    if "scale" in spec:
        item["scale"] = spec["scale"]
    if "platform" in spec:
        item["platform"] = spec["platform"]
        
    images_json.append(item)

appicon_contents = {
    "images": images_json,
    "info": {
        "author": "xcode",
        "version": 1
    }
}

with open(os.path.join(appicon_dir, "Contents.json"), "w") as f:
    json.dump(appicon_contents, f, indent=2)

print(f"Created {len(icon_specs)} icon asset files in {appicon_dir}!")

# 2. Generate Logo ImageSet for LaunchScreen / Splash
logo_specs = [
    ("SpiceMartLogo@1x.png", "1x", 200),
    ("SpiceMartLogo@2x.png", "2x", 400),
    ("SpiceMartLogo@3x.png", "3x", 600)
]

logo_images_json = []
for fn, scale, px in logo_specs:
    out_path = os.path.join(logo_dir, fn)
    subprocess.run(["sips", "-z", str(px), str(px), src_logo, "--out", out_path], check=True)
    logo_images_json.append({
        "filename": fn,
        "idiom": "universal",
        "scale": scale
    })

logo_contents = {
    "images": logo_images_json,
    "info": {
        "author": "xcode",
        "version": 1
    }
}

with open(os.path.join(logo_dir, "Contents.json"), "w") as f:
    json.dump(logo_contents, f, indent=2)

print(f"Created Logo ImageSet in {logo_dir}!")
