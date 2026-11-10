#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
workspace_root="$(cd -- "${script_dir}/.." && pwd)"

if [[ ! -f "${workspace_root}/setup_ekd.bash" ]]; then
  printf 'EKD workspace setup helper not found: %s/setup_ekd.bash\n' "${workspace_root}" >&2
  exit 1
fi

source "${workspace_root}/setup_ekd.bash"

if ! command -v roslaunch >/dev/null 2>&1; then
  printf 'ROS Noetic is not available in this terminal environment.\n' >&2
  exit 1
fi

policy_mode="schedule"
work_start="09:00"
work_end="17:00"
breaks="12:00-13:00"
if [[ -t 0 ]]; then
  printf 'Choose SafeZone policy mode:\n'
  printf '  1) Schedule-based (daily 09:00-17:00; lunch 12:00-13:00; local robot time)\n'
  printf '  2) Work-time demo override (treat scissors/earbuds as prohibited)\n'
  printf '  3) Off-duty demo override (do not apply the work-time prohibition)\n'
  while true; do
    read -r -p 'Select 1, 2, or 3 [1]: ' selection
    selection="${selection:-1}"
    case "${selection}" in
      1)
        policy_mode="schedule"
        printf 'Standard schedule selected: daily 09:00-17:00, lunch 12:00-13:00 (local robot time).\n'
        break
        ;;
      2)
        policy_mode="work"
        printf 'Work-time test override selected; SafeZone will issue work-time reminders for detected targets.\n'
        break
        ;;
      3)
        policy_mode="off_duty"
        printf 'Off-duty test override selected; SafeZone will not apply the work-time prohibition.\n'
        break
        ;;
      *)
        printf 'Please enter 1, 2, or 3.\n'
        ;;
    esac
  done
else
  printf 'Non-interactive launch: using the demo schedule (daily 09:00-17:00, lunch 12:00-13:00, local robot time).\n'
fi

printf '[%s] SafeZone | Starting continuous camera detection. Say a wake phrase to save and send one scene image.\n' \
  "$(date '+%H:%M:%S')"
exec roslaunch jupiterobot2_vision_yolov5 safezone_demo.launch \
  "$@" \
  "policy_mode:=${policy_mode}" \
  "work_start:=${work_start}" \
  "work_end:=${work_end}" \
  "breaks:=${breaks}"
