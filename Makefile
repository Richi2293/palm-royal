# Palm Royal build pipeline.
#
# Nothing here is a binary source. Every .blend and every render is generated
# from the Python scripts in this directory, and the scripts pin their random
# seeds, so a clean checkout rebuilds the same geometry rather than something
# merely similar. Run "make verify" to confirm that.
#
# Blender is located automatically: first on PATH, then at the usual install
# locations on macOS and Linux. Override it when yours lives elsewhere, or when
# you keep several versions around:
#
#     make all BLENDER=/path/to/blender
#
# Tested against Blender 5.1.2. "make check" reports the version in use.

ifeq ($(origin BLENDER), undefined)
BLENDER := $(shell command -v blender 2>/dev/null || \
	for candidate in \
		/Applications/Blender.app/Contents/MacOS/Blender \
		"$$HOME/Applications/Blender.app/Contents/MacOS/Blender" \
		/usr/local/bin/blender \
		/usr/bin/blender \
		/snap/bin/blender \
		/opt/blender/blender; do \
		[ -x "$$candidate" ] && echo "$$candidate" && break; \
	done)
endif
ifeq ($(strip $(BLENDER)),)
BLENDER := blender
endif

ifeq ($(origin PYTHON), undefined)
PYTHON := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python3)
endif

RUN = "$(BLENDER)" --background --factory-startup --python

DIORAMA   = palm-royal.blend
CITY      = coastal-city.blend
DETAILED  = coastal-city-detailed.blend
INTERIORS = coastal-city-interiors.blend
NEON      = coastal-city-neon.blend

SCENES = $(DIORAMA) $(CITY) $(DETAILED) $(INTERIORS) $(NEON)

ASSET_MANIFEST = assets/download-manifest.json
CAFE_ASSET     = assets/croissant/croissant.blend

.PHONY: help all diorama city detailed interiors neon assets verify clean check
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:

help:
	@echo "Palm Royal, a Blender city defined entirely by code."
	@echo ""
	@echo "Targets, in pipeline order. Each one depends on the previous scene,"
	@echo "so asking for a later stage builds everything it needs first."
	@echo ""
	@echo "  make assets     download the CC0 and CC BY source assets (~500 MB)"
	@echo "  make diorama    build Palm Royal, the standalone street diorama"
	@echo "  make city       build the coastal city layout"
	@echo "  make detailed   add the showcase hotel, cafe and PBR detail"
	@echo "  make interiors  cut real window openings and furnish the cafe"
	@echo "  make neon       add the Art Deco neon sign"
	@echo "  make all        the whole pipeline, from assets to neon"
	@echo ""
	@echo "  make verify     check every built scene against its reference counts"
	@echo "  make check      confirm Blender is where the build expects it"
	@echo "  make clean      delete the generated .blend files (renders are kept)"
	@echo ""
	@echo "Blender in use: $(BLENDER)"
	@echo "Override with:   make <target> BLENDER=/path/to/blender"

all: neon diorama

check:
	@command -v "$(BLENDER)" >/dev/null 2>&1 || { \
	  echo "Blender not found."; \
	  echo ""; \
	  echo "Looked on PATH and at the usual macOS and Linux install locations."; \
	  echo "Install Blender, or point the build at your copy:"; \
	  echo "    make all BLENDER=/path/to/blender"; \
	  echo ""; \
	  echo "On Windows, run make from Git Bash or WSL and pass the executable:"; \
	  echo "    make all BLENDER='/c/Program Files/Blender Foundation/Blender 5.1/blender.exe'"; \
	  exit 1; }
	@$(RUN) check_blender.py 2>/dev/null | grep -E "supported|Warning:" || { \
	  echo "Blender at '$(BLENDER)' failed the version check:"; \
	  $(RUN) check_blender.py 2>&1 | tail -12; \
	  exit 1; }

# ---------------------------------------------------------------- source assets

assets: $(ASSET_MANIFEST) $(CAFE_ASSET)

$(ASSET_MANIFEST): download_assets.py
	$(PYTHON) download_assets.py

$(CAFE_ASSET): download_cafe_assets.py
	$(PYTHON) download_cafe_assets.py

# ---------------------------------------------------------------------- scenes

diorama: $(DIORAMA)
city: $(CITY)
detailed: $(DETAILED)
interiors: $(INTERIORS)
neon: $(NEON)

# Standalone: procedural geometry only, no downloaded assets required.
$(DIORAMA): build_world.py | check
	$(RUN) build_world.py

$(CITY): build_city.py refine_city.py build_world.py | check
	$(RUN) build_city.py
	$(RUN) refine_city.py

# Replaces the central block with detailed architecture and scanned PBR assets.
$(DETAILED): $(CITY) $(ASSET_MANIFEST) build_showcase.py refine_showcase.py finalize_showcase.py prepare_navigation.py | check
	$(RUN) build_showcase.py
	$(RUN) refine_showcase.py
	$(RUN) finalize_showcase.py
	$(RUN) prepare_navigation.py

$(INTERIORS): $(DETAILED) $(CAFE_ASSET) upgrade_windows_cafe.py | check
	$(RUN) upgrade_windows_cafe.py

$(NEON): $(INTERIORS) upgrade_sign.py | check
	$(RUN) upgrade_sign.py

# ---------------------------------------------------------------------- checks

verify: verify_scene.py
	@for scene in $(SCENES); do \
	  if [ -f "$$scene" ]; then \
	    $(RUN) verify_scene.py -- "$$scene" 2>/dev/null | grep -E "Verifying|ok$$|MISMATCH|matches|reference" || exit 1; \
	  else \
	    echo "$$scene not built yet, skipping."; \
	  fi; \
	done

# ---------------------------------------------------------------- housekeeping

# Removes generated scenes and the intermediate backups the scripts write.
# Downloaded assets and committed renders are left alone: use "make assets" to
# refetch the former, and they are large.
clean:
	rm -f $(SCENES) *.blend1
	rm -f coastal-city-before-detail.blend palm-royal-before-expansion.blend \
	      detailed-before-navigation.blend detailed-before-interiors.blend \
	      interiors-before-neon.blend previous-session.blend
	@echo "Generated scenes removed. Rebuild them with: make all"
