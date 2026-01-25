WeasyPrint setup and system dependencies

WeasyPrint requires native system libraries (C libraries) in addition to the Python package. Below are recommended install steps for common platforms.

Debian / Ubuntu (apt)

```bash
# Install required system packages
sudo apt update && sudo apt install -y \
  build-essential \
  libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0 libffi-dev \
  libjpeg-dev libpng-dev libpangocairo-1.0-0 \
  fonts-dejavu-core fonts-liberation fonts-noto-core

# Optional: add additional fonts
sudo apt install -y fonts-noto-extra fonts-roboto

# Then install the Python dependency
pip install -r requirements.txt
```

Fedora / RHEL / CentOS (dnf/yum)

```bash
sudo dnf install -y \
  cairo pango gdk-pixbuf2 libffi-devel \
  libjpeg-turbo-devel libpng-devel \
  dejavu-sans-fonts liberation-fonts noto-sans-fonts

pip install -r requirements.txt
```

macOS (Homebrew)

```bash
brew install cairo pango gdk-pixbuf libffi
brew install fontconfig
pip install -r requirements.txt
```

Notes
- WeasyPrint relies on Cairo + Pango + GDK-PixBuf for rendering. Installing the packages above is usually sufficient.
- Ensure you have a reasonable set of fonts installed on the server so generated PDFs render with appropriate glyphs.
- If you deploy inside Docker, add the above packages to your Dockerfile. Example (Debian-based image):

```dockerfile
RUN apt-get update && apt-get install -y \
    libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0 libffi-dev \
    fonts-dejavu-core fonts-liberation
```

Troubleshooting
- If PDF generation fails, examine the server logs for WeasyPrint exceptions (we log exceptions when PDF generation fails and fall back to HTML).
- Use the provided script `scripts/check_weasyprint.sh` to verify the runtime environment (checks for `pkg-config` probes and Python import).

References
- WeasyPrint documentation: https://weasyprint.org/docs/
- Troubleshooting: https://weasyprint.org/docs/troubleshooting/
