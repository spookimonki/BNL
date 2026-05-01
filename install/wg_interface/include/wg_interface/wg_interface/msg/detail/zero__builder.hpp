// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from wg_interface:msg/Zero.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wg_interface/msg/zero.hpp"


#ifndef WG_INTERFACE__MSG__DETAIL__ZERO__BUILDER_HPP_
#define WG_INTERFACE__MSG__DETAIL__ZERO__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "wg_interface/msg/detail/zero__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace wg_interface
{

namespace msg
{


}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::wg_interface::msg::Zero>()
{
  return ::wg_interface::msg::Zero(rosidl_runtime_cpp::MessageInitialization::ZERO);
}

}  // namespace wg_interface

#endif  // WG_INTERFACE__MSG__DETAIL__ZERO__BUILDER_HPP_
