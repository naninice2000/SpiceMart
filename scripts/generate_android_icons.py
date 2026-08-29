import os
import subprocess

src_icon = "images/FavIcon.png"
src_logo = "images/SpiceMartLogo.png"
res_dir = "android/app/src/main/res"

mipmap_densities = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}

drawable_densities = {
    "drawable-mdpi": 108,
    "drawable-hdpi": 162,
    "drawable-xhdpi": 216,
    "drawable-xxhdpi": 324,
    "drawable-xxxhdpi": 432,
}

print("1. Creating mipmap density folders and icons...")
for folder, size in mipmap_densities.items():
    target_dir = os.path.join(res_dir, folder)
    os.makedirs(target_dir, exist_ok=True)
    
    # Generate ic_launcher.png
    out_launcher = os.path.join(target_dir, "ic_launcher.png")
    subprocess.run(["sips", "-z", str(size), str(size), src_icon, "--out", out_launcher], check=True)
    
    # Generate ic_launcher_round.png
    out_round = os.path.join(target_dir, "ic_launcher_round.png")
    subprocess.run(["sips", "-z", str(size), str(size), src_icon, "--out", out_round], check=True)
    print(f"Generated {folder} ({size}x{size})")

print("2. Creating adaptive foreground drawables...")
for folder, size in drawable_densities.items():
    target_dir = os.path.join(res_dir, folder)
    os.makedirs(target_dir, exist_ok=True)
    out_fg = os.path.join(target_dir, "ic_launcher_foreground.png")
    subprocess.run(["sips", "-z", str(size), str(size), src_icon, "--out", out_fg], check=True)

# Generate high-res splash icon
splash_dir = os.path.join(res_dir, "drawable")
os.makedirs(splash_dir, exist_ok=True)
splash_out = os.path.join(splash_dir, "splash_icon.png")
subprocess.run(["sips", "-z", "512", "512", src_icon, "--out", splash_out], check=True)

logo_out = os.path.join(splash_dir, "app_logo.png")
subprocess.run(["sips", "-z", "512", "512", src_logo, "--out", logo_out], check=True)

print("All Android icons successfully generated!")
