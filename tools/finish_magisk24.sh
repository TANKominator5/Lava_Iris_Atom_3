#!/system/bin/sh
# Review before use. No flashing, deletion, reboot or automatic permission grant.
set -eu
if [ "$#" -ne 4 ] || [ "$1" != --apply ]; then
    echo "Usage: sh finish_magisk24.sh --apply /absolute/extracted-tools /absolute/original_boot.img EXPECTED_ORIGINAL_SHA256"
    exit 2
fi
TOOLS=$2
ORIGINAL=$3
EXPECTED=$4
case "$TOOLS:$ORIGINAL" in
    /*:/*) ;;
    *) echo "Absolute paths required"; exit 2 ;;
esac
BB=$TOOLS/busybox
test -x "$BB"
test "$("$BB" id -u)" = 0
case "$EXPECTED" in *[!0-9a-f]*|'') echo "Lowercase SHA-256 required"; exit 2 ;; esac
test "${#EXPECTED}" -eq 64
test "$("$BB" stat -c %s "$ORIGINAL")" = 12582912
ACTUAL=$("$BB" sha256sum "$ORIGINAL")
test "${ACTUAL%% *}" = "$EXPECTED"
test "$(/sbin/magisk -v)" = '24.3:MAGISK'
test "$("$TOOLS/magisk" -c)" = '24.3:MAGISK'
grep -x "MAGISK_VER='24.3'" "$TOOLS/util_functions.sh"
grep -x 'MAGISK_VER_CODE=24300' "$TOOLS/util_functions.sh"
for FILE in busybox magiskboot magiskinit magisk32 magisk util_functions.sh boot_patch.sh addon.d.sh; do
    test -f "$TOOLS/$FILE"
    test ! -L "$TOOLS/$FILE"
done
# Preflight policy state before making environment changes.
if [ -L /data/adb/magisk/magiskpolicy ]; then
    test "$("$BB" readlink /data/adb/magisk/magiskpolicy)" = ./magiskinit
elif [ -e /data/adb/magisk/magiskpolicy ]; then
    echo "Existing magiskpolicy binary needs manual review; no automatic replacement"
    exit 1
fi
SHA1=$("$BB" sha1sum "$ORIGINAL")
SHA1=${SHA1%% *}
BACKUP=/data/magisk_backup_$SHA1
test ! -L /data/adb
test ! -L /data/adb/magisk
test ! -L "$BACKUP"
mkdir -p /data/adb/magisk "$BACKUP"
chmod 700 /data/adb "$BACKUP"
if [ -e "$BACKUP/boot.img.gz" ]; then
    test ! -L "$BACKUP/boot.img.gz"
    PREVIOUS=$("$BB" gzip -dc "$BACKUP/boot.img.gz" | "$BB" sha256sum)
    test "${PREVIOUS%% *}" = "$EXPECTED"
else
    # Noclobber avoids replacing a backup created by another process.
    (set -C; "$BB" gzip -c "$ORIGINAL" > "$BACKUP/boot.img.gz")
fi
chmod 600 "$BACKUP/boot.img.gz"
for FILE in busybox magiskboot magiskinit magisk32 magisk util_functions.sh boot_patch.sh addon.d.sh; do
    test ! -L "/data/adb/magisk/$FILE"
    cp "$TOOLS/$FILE" "/data/adb/magisk/$FILE"
    chown 0:0 "/data/adb/magisk/$FILE"
    chmod 755 "/data/adb/magisk/$FILE"
done
# Refuse an unexpected existing policy binary rather than overwriting it blindly.
if [ -L /data/adb/magisk/magiskpolicy ]; then
    test "$("$BB" readlink /data/adb/magisk/magiskpolicy)" = ./magiskinit
elif [ ! -e /data/adb/magisk/magiskpolicy ]; then
    ln -s ./magiskinit /data/adb/magisk/magiskpolicy
else
    echo "Policy path changed during setup; stop for manual review"
    exit 1
fi
/sbin/magisk --restorecon
sync
echo "Matching v24.3 environment and original backup prepared; no boot partition was written"
