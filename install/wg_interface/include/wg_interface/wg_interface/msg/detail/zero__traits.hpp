// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from wg_interface:msg/Zero.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wg_interface/msg/zero.hpp"


#ifndef WG_INTERFACE__MSG__DETAIL__ZERO__TRAITS_HPP_
#define WG_INTERFACE__MSG__DETAIL__ZERO__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "wg_interface/msg/detail/zero__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace wg_interface
{

namespace msg
{

inline void to_flow_style_yaml(
  const Zero & msg,
  std::ostream & out)
{
  (void)msg;
  out << "null";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Zero & msg,
  std::ostream & out, size_t indentation = 0)
{
  (void)msg;
  (void)indentation;
  out << "null\n";
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Zero & msg, bool use_flow_style = false)
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
  const wg_interface::msg::Zero & msg,
  std::ostream & out, size_t indentation = 0)
{
  wg_interface::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use wg_interface::msg::to_yaml() instead")]]
inline std::string to_yaml(const wg_interface::msg::Zero & msg)
{
  return wg_interface::msg::to_yaml(msg);
}

template<>
inline const char * data_type<wg_interface::msg::Zero>()
{
  return "wg_interface::msg::Zero";
}

template<>
inline const char * name<wg_interface::msg::Zero>()
{
  return "wg_interface/msg/Zero";
}

template<>
struct has_fixed_size<wg_interface::msg::Zero>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<wg_interface::msg::Zero>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<wg_interface::msg::Zero>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // WG_INTERFACE__MSG__DETAIL__ZERO__TRAITS_HPP_
