import "./scss/main.scss";

import React from "react";
import ReactDOM from "react-dom";

import BookingControl from "./js/BookingControl";

ReactDOM.render(
  <BookingControl attendance={attendance} bookables={bookables} />,
  document.getElementById("booking-control")
);
