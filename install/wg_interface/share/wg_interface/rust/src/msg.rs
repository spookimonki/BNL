#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to wg_interface__msg__Zero
/// bare en placeholder fil intil videre

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Zero {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for Zero {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Zero::default())
  }
}

impl rosidl_runtime_rs::Message for Zero {
  type RmwMsg = super::msg::rmw::Zero;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to wg_interface__msg__ControlEvent

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ControlEvent {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,

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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::ControlEvent::default())
  }
}

impl rosidl_runtime_rs::Message for ControlEvent {
  type RmwMsg = super::msg::rmw::ControlEvent;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        control_type: msg.control_type,
        right_cycle: msg.right_cycle,
        right_direction: msg.right_direction,
        left_cycle: msg.left_cycle,
        left_direction: msg.left_direction,
        combined_cycle: msg.combined_cycle,
        combined_direction: msg.combined_direction,
        combined_rotation: msg.combined_rotation,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
      control_type: msg.control_type,
      right_cycle: msg.right_cycle,
      right_direction: msg.right_direction,
      left_cycle: msg.left_cycle,
      left_direction: msg.left_direction,
      combined_cycle: msg.combined_cycle,
      combined_direction: msg.combined_direction,
      combined_rotation: msg.combined_rotation,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      control_type: msg.control_type,
      right_cycle: msg.right_cycle,
      right_direction: msg.right_direction,
      left_cycle: msg.left_cycle,
      left_direction: msg.left_direction,
      combined_cycle: msg.combined_cycle,
      combined_direction: msg.combined_direction,
      combined_rotation: msg.combined_rotation,
    }
  }
}


