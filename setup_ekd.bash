if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  printf 'Source this file in Bash: source %s\n' "$0" >&2
  exit 2
fi

_ekd_workspace_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)" || return 1

if [[ ! -f /opt/ros/noetic/setup.bash ]]; then
  printf 'ROS Noetic setup not found at /opt/ros/noetic/setup.bash\n' >&2
  return 1
fi

if [[ ! -f "${_ekd_workspace_root}/devel/setup.bash" ]]; then
  printf 'EKD workspace is not built yet: %s/devel/setup.bash is missing\n' "${_ekd_workspace_root}" >&2
  unset _ekd_workspace_root
  return 1
fi

source /opt/ros/noetic/setup.bash || return 1
source "${_ekd_workspace_root}/devel/setup.bash" || return 1
if [[ -f "${_ekd_workspace_root}/.env" ]]; then
  source "${_ekd_workspace_root}/.env" || return 1
fi
export EKD_CATKIN_WS="${_ekd_workspace_root}"
unset _ekd_workspace_root