// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from wg_interface:msg/ControlEvent.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wg_interface/msg/control_event.hpp"


#ifndef WG_INTERFACE__MSG__DETAIL__CONTROL_EVENT__TRAITS_HPP_
#define WG_INTERFACE__MSG__DETAIL__CONTROL_EVENT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "wg_interface/msg/detail/control_event__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace wg_interface
{

namespace msg
{

inline void to_flow_style_yaml(
  const ControlEvent & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: control_type
  {
    out << "control_type: ";
    rosidl_generator_traits::value_to_yaml(msg.control_type, out);
    out << ", ";
  }

  // member: right_cycle
  {
    out << "right_cycle: ";
    rosidl_generator_traits::value_to_yaml(msg.right_cycle, out);
    out << ", ";
  }

  // member: right_direction
  {
    out << "right_direction: ";
    rosidl_generator_traits::value_to_yaml(msg.right_direction, out);
    out << ", ";
  }

  // member: left_cycle
  {
    out << "left_cycle: ";
    rosidl_generator_traits::value_to_yaml(msg.left_cycle, out);
    out << ", ";
  }

  // member: left_direction
  {
    out << "left_direction: ";
    rosidl_generator_traits::value_to_yaml(msg.left_direction, out);
    out << ", ";
  }

  // member: combined_cycle
  {
    out << "combined_cycle: ";
    rosidl_generator_traits::value_to_yaml(msg.combined_cycle, out);
    out << ", ";
  }

  // member: combined_direction
  {
    out << "combined_direction: ";
    rosidl_generator_traits::value_to_yaml(msg.combined_direction, out);
    out << ", ";
  }

  // member: combined_rotation
  {
    out << "combined_rotation: ";
    rosidl_generator_traits::value_to_yaml(msg.combined_rotation, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ControlEvent & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: control_type
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "control_type: ";
    rosidl_generator_traits::value_to_yaml(msg.control_type, out);
    out << "\n";
  }

  // member: right_cycle
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "right_cycle: ";
    rosidl_generator_traits::value_to_yaml(msg.right_cycle, out);
    out << "\n";
  }

  // member: right_direction
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "right_direction: ";
    rosidl_generator_traits::value_to_yaml(msg.right_direction, out);
    out << "\n";
  }

  // member: left_cycle
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "left_cycle: ";
    rosidl_generator_traits::value_to_yaml(msg.left_cycle, out);
    out << "\n";
  }

  // member: left_direction
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "left_direction: ";
    rosidl_generator_traits::value_to_yaml(msg.left_direction, out);
    out << "\n";
  }

  // member: combined_cycle
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "combined_cycle: ";
    rosidl_generator_traits::value_to_yaml(msg.combined_cycle, out);
    out << "\n";
  }

  // member: combined_direction
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "combined_direction: ";
    rosidl_generator_traits::value_to_yaml(msg.combined_direction, out);
    out << "\n";
  }

  // member: combined_rotation
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "combined_rotation: ";
    rosidl_generator_traits::value_to_yaml(msg.combined_rotation, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ControlEvent & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace wg_interface

namespace rosidl_generator_traits
{

[[deprecated("use wg_interface::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const wg_interface::msg::ControlEvent & msg,
  std::ostream & out, size_t indentation = 0)
{
  wg_interface::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use wg_interface::msg::to_yaml() instead")]]
inline std::string to_yaml(const wg_interface::msg::ControlEvent & msg)
{
  return wg_interface::msg::to_yaml(msg);
}

template<>
inline const char * data_type<wg_interface::msg::ControlEvent>()
{
  return "wg_interface::msg::ControlEvent";
}

template<>
inline const char * name<wg_interface::msg::ControlEvent>()
{
  return "wg_interface/msg/ControlEvent";
}

template<>
struct has_fixed_size<wg_interface::msg::ControlEvent>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<wg_interface::msg::ControlEvent>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<wg_interface::msg::ControlEvent>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // WG_INTERFACE__MSG__DETAIL__CONTROL_EVENT__TRAITS_HPP_
