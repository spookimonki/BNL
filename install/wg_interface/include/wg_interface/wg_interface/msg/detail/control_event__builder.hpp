// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from wg_interface:msg/ControlEvent.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wg_interface/msg/control_event.hpp"


#ifndef WG_INTERFACE__MSG__DETAIL__CONTROL_EVENT__BUILDER_HPP_
#define WG_INTERFACE__MSG__DETAIL__CONTROL_EVENT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "wg_interface/msg/detail/control_event__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace wg_interface
{

namespace msg
{

namespace builder
{

class Init_ControlEvent_combined_rotation
{
public:
  explicit Init_ControlEvent_combined_rotation(::wg_interface::msg::ControlEvent & msg)
  : msg_(msg)
  {}
  ::wg_interface::msg::ControlEvent combined_rotation(::wg_interface::msg::ControlEvent::_combined_rotation_type arg)
  {
    msg_.combined_rotation = std::move(arg);
    return std::move(msg_);
  }

private:
  ::wg_interface::msg::ControlEvent msg_;
};

class Init_ControlEvent_combined_direction
{
public:
  explicit Init_ControlEvent_combined_direction(::wg_interface::msg::ControlEvent & msg)
  : msg_(msg)
  {}
  Init_ControlEvent_combined_rotation combined_direction(::wg_interface::msg::ControlEvent::_combined_direction_type arg)
  {
    msg_.combined_direction = std::move(arg);
    return Init_ControlEvent_combined_rotation(msg_);
  }

private:
  ::wg_interface::msg::ControlEvent msg_;
};

class Init_ControlEvent_combined_cycle
{
public:
  explicit Init_ControlEvent_combined_cycle(::wg_interface::msg::ControlEvent & msg)
  : msg_(msg)
  {}
  Init_ControlEvent_combined_direction combined_cycle(::wg_interface::msg::ControlEvent::_combined_cycle_type arg)
  {
    msg_.combined_cycle = std::move(arg);
    return Init_ControlEvent_combined_direction(msg_);
  }

private:
  ::wg_interface::msg::ControlEvent msg_;
};

class Init_ControlEvent_left_direction
{
public:
  explicit Init_ControlEvent_left_direction(::wg_interface::msg::ControlEvent & msg)
  : msg_(msg)
  {}
  Init_ControlEvent_combined_cycle left_direction(::wg_interface::msg::ControlEvent::_left_direction_type arg)
  {
    msg_.left_direction = std::move(arg);
    return Init_ControlEvent_combined_cycle(msg_);
  }

private:
  ::wg_interface::msg::ControlEvent msg_;
};

class Init_ControlEvent_left_cycle
{
public:
  explicit Init_ControlEvent_left_cycle(::wg_interface::msg::ControlEvent & msg)
  : msg_(msg)
  {}
  Init_ControlEvent_left_direction left_cycle(::wg_interface::msg::ControlEvent::_left_cycle_type arg)
  {
    msg_.left_cycle = std::move(arg);
    return Init_ControlEvent_left_direction(msg_);
  }

private:
  ::wg_interface::msg::ControlEvent msg_;
};

class Init_ControlEvent_right_direction
{
public:
  explicit Init_ControlEvent_right_direction(::wg_interface::msg::ControlEvent & msg)
  : msg_(msg)
  {}
  Init_ControlEvent_left_cycle right_direction(::wg_interface::msg::ControlEvent::_right_direction_type arg)
  {
    msg_.right_direction = std::move(arg);
    return Init_ControlEvent_left_cycle(msg_);
  }

private:
  ::wg_interface::msg::ControlEvent msg_;
};

class Init_ControlEvent_right_cycle
{
public:
  explicit Init_ControlEvent_right_cycle(::wg_interface::msg::ControlEvent & msg)
  : msg_(msg)
  {}
  Init_ControlEvent_right_direction right_cycle(::wg_interface::msg::ControlEvent::_right_cycle_type arg)
  {
    msg_.right_cycle = std::move(arg);
    return Init_ControlEvent_right_direction(msg_);
  }

private:
  ::wg_interface::msg::ControlEvent msg_;
};

class Init_ControlEvent_control_type
{
public:
  explicit Init_ControlEvent_control_type(::wg_interface::msg::ControlEvent & msg)
  : msg_(msg)
  {}
  Init_ControlEvent_right_cycle control_type(::wg_interface::msg::ControlEvent::_control_type_type arg)
  {
    msg_.control_type = std::move(arg);
    return Init_ControlEvent_right_cycle(msg_);
  }

private:
  ::wg_interface::msg::ControlEvent msg_;
};

class Init_ControlEvent_header
{
public:
  Init_ControlEvent_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ControlEvent_control_type header(::wg_interface::msg::ControlEvent::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_ControlEvent_control_type(msg_);
  }

private:
  ::wg_interface::msg::ControlEvent msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::wg_interface::msg::ControlEvent>()
{
  return wg_interface::msg::builder::Init_ControlEvent_header();
}

}  // namespace wg_interface

#endif  // WG_INTERFACE__MSG__DETAIL__CONTROL_EVENT__BUILDER_HPP_
