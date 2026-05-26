SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/install/setup.bash"
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export GZ_SIM_RESOURCE_PATH="$SCRIPT_DIR/src/gazebo_sim/models"
export CYCLONEDDS_URI="file://$SCRIPT_DIR/config/cyclonedds.xml"
