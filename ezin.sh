#!/bin/bash

# ==========================================
# ezin (Easy Install)
# ==========================================

require_root() {
  if [ "$EUID" -ne 0 ]; then
    echo "Error: Please run this script as root (use sudo)."
    exit 1
  fi
}

setup_target_file() {
  FILEPATH="$1"
  if [ -z "$FILEPATH" ]; then
    read -p "Enter the full path to the zip or tarball file: " FILEPATH
  fi

  if [ ! -f "$FILEPATH" ]; then
    echo "Error: File '$FILEPATH' does not exist."
    exit 1
  fi

  local mime_type
  mime_type=$(file -b --mime-type "$FILEPATH")
  IS_ZIP=false
  IS_TAR=false

  if [[ "$mime_type" == "application/zip" ]]; then
    IS_ZIP=true
  elif [[ "$mime_type" == "application/x-tar" || "$mime_type" == "application/gzip" || "$mime_type" == "application/x-xz" || "$mime_type" == "application/x-bzip2" ]]; then
    IS_TAR=true
  else
    echo "Error: File is not a valid zip or tar archive. Detected MIME type: $mime_type"
    exit 1
  fi
}

extract_archive() {
  echo "Extracting archive..."
  TMP_DIR=$(mktemp -d)

  if [ "$IS_ZIP" = true ]; then
    unzip -q "$FILEPATH" -d "$TMP_DIR"
  elif [ "$IS_TAR" = true ]; then
    tar -xf "$FILEPATH" -C "$TMP_DIR"
  fi

  if [ $? -ne 0 ]; then
    echo "Error: Extraction failed."
    rm -rf "$TMP_DIR"
    exit 1
  fi

  # Determine extraction structure
  local item_count
  item_count=$(ls -1A "$TMP_DIR" | wc -l)
  
  if [ "$item_count" -eq 1 ] && [ -d "$TMP_DIR/$(ls -A "$TMP_DIR")" ]; then
    local extracted_name
    extracted_name=$(ls -A "$TMP_DIR")
    SOURCE_DIR="$TMP_DIR/$extracted_name"
    EXTRACTED_FOLDER_NAME="$extracted_name"
  else
    EXTRACTED_FOLDER_NAME=$(basename "$FILEPATH" | sed -E 's/\.(tar\.gz|tar\.xz|tar\.bz2|tgz|zip)$//i')
    SOURCE_DIR="$TMP_DIR"
  fi

  TARGET_OPT_DIR="/opt/$EXTRACTED_FOLDER_NAME"
}

move_to_opt() {
  echo "Moving extracted files to $TARGET_OPT_DIR..."
  
  if [ -d "$TARGET_OPT_DIR" ]; then
    local overwrite="N"
    read -p "Warning: $TARGET_OPT_DIR already exists. Overwrite? [y/N] " overwrite
    if [[ "${overwrite,,}" != "y" ]]; then
      echo -e "Aborting..."
      rm -rf "$TMP_DIR"
      exit 1
    fi
    echo -e "Overwriting..."
    rm -rf "$TARGET_OPT_DIR"
  fi
  
  mv "$SOURCE_DIR" "$TARGET_OPT_DIR"
  rm -rf "$TMP_DIR" # Cleanup temporary directory
}

setup_desktop_file() {
  local desktop_system_dir="/usr/share/applications"
  local found_desktop
  found_desktop=$(find "$TARGET_OPT_DIR" -maxdepth 3 -type f -name "*.desktop" | head -n 1)
  local create_desktop="N"

  if [ -n "$found_desktop" ]; then
    local desktop_filename
    desktop_filename=$(basename "$found_desktop")
    echo -e "\n--- Pre-existing .desktop file found: $desktop_filename ---"
    
    local final_desktop_path="$desktop_system_dir/$desktop_filename"
    cp "$found_desktop" "$final_desktop_path"

    # Replacing relative paths
    sed -i "s|^Exec=\./|Exec=$TARGET_OPT_DIR/|g" "$final_desktop_path"
    sed -i "s|^Exec=bin/|Exec=$TARGET_OPT_DIR/bin/|g" "$final_desktop_path"
    sed -i "s|^Icon=\./|Icon=$TARGET_OPT_DIR/|g" "$final_desktop_path"

    echo "Fixed any relative paths inside the file."
    cat "$final_desktop_path"
    echo "---------------------------------------------------"

    chown root:root "$final_desktop_path"
    chmod 644 "$final_desktop_path"
    update-desktop-database "$desktop_system_dir"
    echo -e "\nDesktop file successfully installed to: $final_desktop_path"
    
  else
    read -p $'\nNo .desktop file found. Create one? [y/N] ' create_desktop
    if [[ "${create_desktop,,}" == "y" ]]; then
      local app_name app_comment app_exec app_icon app_cat
      read -p "Application Name (e.g., My App): " app_name
      read -p "Comment (e.g., A useful tool): " app_comment
      read -p "Executable Command/Path (e.g., $TARGET_OPT_DIR/bin/app): " app_exec
      read -p "Icon Name or Path (e.g., utilities-terminal): " app_icon
      read -p "Categories (e.g., Development;Utility;): " app_cat

      local desktop_filename
      desktop_filename="$(echo "$app_name" | tr '[:upper:]' '[:lower:]' | tr -s ' ' '-').desktop"
      local final_desktop_path="$desktop_system_dir/$desktop_filename"

      cat <<EOF > "$final_desktop_path"
[Desktop Entry]
Type=Application
Name=$app_name
Comment=$app_comment
Exec=$app_exec
Icon=$app_icon
Categories=$app_cat
Terminal=false
EOF
    
      echo -e "\n--- Created new .desktop file ---"
      cat "$final_desktop_path"
      echo "---------------------------------"

      chown root:root "$final_desktop_path"
      chmod 644 "$final_desktop_path"
      update-desktop-database "$desktop_system_dir"
      echo -e "\nDesktop file successfully installed to: $final_desktop_path"
    fi
  fi
}

setup_bashrc_path() {
  local add_path="N"
  echo ""
  read -p "Do you want to add the binary directory to your PATH in ~/.bashrc? [y/N] " add_path
  
  if [[ "${add_path,,}" == "y" ]]; then
    local target_bashrc
    if [ -n "$SUDO_USER" ]; then
      local user_home
      user_home=$(getent passwd "$SUDO_USER" | cut -d: -f6)
      target_bashrc="$user_home/.bashrc"
    else
      target_bashrc="$HOME/.bashrc"
    fi

    local binary_dir
    read -p "Enter the full path to the binary directory (e.g., $TARGET_OPT_DIR/bin): " binary_dir
    
    if [ ! -d "$binary_dir" ]; then
      echo "Error: Directory not found at '$binary_dir'. Skipping PATH addition."
      echo "Add it manually at $target_bashrc"
    else
      if grep -q "export PATH=\$PATH:$binary_dir" "$target_bashrc"; then
        echo -e "\nDirectory '$binary_dir' is already in your $target_bashrc."
      else
        echo "" >> "$target_bashrc"
        echo "# Added by ezin tool" >> "$target_bashrc"
        echo "export PATH=\$PATH:$binary_dir" >> "$target_bashrc"
        
        if [ -n "$SUDO_USER" ]; then
          chown "$SUDO_USER" "$target_bashrc"
        fi
        
        echo -e "\nSuccessfully added '$binary_dir' to $target_bashrc!"
        echo -e "--------------------------------------------------------"
        echo -e "   IMPORTANT: To apply this immediately, run:"
        echo -e "   source ~/.bashrc"
        echo -e "--------------------------------------------------------"
      fi
    fi
  fi
}

# ==========================================
# Main Execution Loop
# ==========================================
main() {
  require_root
  setup_target_file "$1"
  extract_archive
  move_to_opt
  setup_desktop_file
  setup_bashrc_path
  
  echo -e "\nInstallation Complete!"
}

main "$@"
