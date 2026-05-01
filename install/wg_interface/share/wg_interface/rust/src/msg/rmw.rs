#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "wg_interface__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__wg_interface__msg__Zero() -> *const std::ffi::c_void;
}

#[link(name = "wg_interface__rosidl_generator_c")]
extern "C" {
    fn wg_interface__msg__Zero__init(msg: *mut Zero) -> bool;
    fn wg_interface__msg__Zero__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Zero>, size: usize) -> bool;
    fn wg_interface__msg__Zero__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Zero>);
    fn wg_interface__msg__Zero__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Zero>, out_seq: *mut rosidl_runtime_rs::Sequence<Zero>) -> bool;
}

// Corresponds to wg_interface__msg__Zero
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// bare en placeholder fil intil videre

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Zero {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for Zero {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !wg_interface__msg__Zero__init(&mut msg as *mut _) {
        panic!("Call to wg_interface__msg__Zero__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Zero {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { wg_interface__msg__Zero__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { wg_interface__msg__Zero__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { wg_interface__msg__Zero__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Zero {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Zero where Self: Sized {
  const TYPE_NAME: &'static str = "wg_interface/msg/Zero";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__wg_interface__msg__Zero() }
  }
}


#[link(name = "wg_interface__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__wg_interface__msg__ControlEvent() -> *const std::ffi::c_void;
}

#[link(name = "wg_interface__rosidl_generator_c")]
extern "C" {
    fn wg_interface__msg__ControlEvent__init(msg: *mut ControlEvent) -> bool;
    fn wg_interface__msg__ControlEvent__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ControlEvent>, size: usize) -> bool;
    fn wg_interface__msg__ControlEvent__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ControlEvent>);
    fn wg_interface__msg__ControlEvent__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ControlEvent>, out_seq: *mut rosidl_runtime_rs::Sequence<ControlEvent>) -> bool;
}

// Corresponds to wg_interface__msg__ControlEvent
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ControlEvent {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// Hvilken type signal du sender
    pub control_type: u8,

    /// prosent hvor mye av maks frekvens (hel prosent 50% = 50)
    pub right_cycle: f64,

    /// tall som representerer retningen på motoren 0, 1
    pub right_direction: u8,

    /// prosent hvor mye av maks frekvens (hel prosent 50% = 50)
    pub left_cycle: f64,

    /// tall som representerer retningen på motoren 0, 1
    pub left_direction: u8,

    /// prosent hvor mye av maks frekvens (hel prosent 50% = 50)
    pub combined_cycle: f64,

    /// tall som representerer retning 0, 1
    pub combined_direction: u8,

    /// 0 = mot klokka, 1 = med klokka
    pub combined_rotation: u8,

}



impl Default for ControlEvent {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !wg_interface__msg__ControlEvent__init(&mut msg as *mut _) {
        panic!("Call to wg_interface__msg__ControlEvent__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ControlEvent {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { wg_interface__msg__ControlEvent__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { wg_interface__msg__ControlEvent__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { wg_interface__msg__ControlEvent__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ControlEvent {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ControlEvent where Self: Sized {
  const TYPE_NAME: &'static str = "wg_interface/msg/ControlEvent";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__wg_interface__msg__ControlEvent() }
  }
}


