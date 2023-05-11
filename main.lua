-- Set the path to the log file
local utils = require("mp.utils")

local log_file_path = utils.join_path(mp.find_config_file("."), "hey.log")
-- Function to write the log data to the file
function write_log_file()
  local f = io.open(log_file_path, "a")
  local media_title = mp.get_property("media-title")
  local media_path = mp.get_property("path")
  local filename = mp.get_property("filename")
  local media_duration = mp.get_property_number("duration")
  local media_time_pos = mp.get_property_number("time-pos")
  local date_time = os.date("%Y-%m-%dT%H:%M:%S")
  f:write(string.format("%s\t%s\t%s\t%s\n", date_time, filename, media_time_pos, media_duration))
  f:close()
end

-- Register the function to be called when MPV is closed
--
mp.add_hook("on_unload", 9, write_log_file)
-- mp.register_event("shutdown", write_log_file)
