import React from "react";

import Hour from "./Hour";
import BookingForm from "./BookingForm";

function Day(props) {
  let options = {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  const dateDisplay = new Date(props.date).toLocaleString("de-DE", options);

  const bookingForm = props.selectedHour && (
    <BookingForm
      selectedDate={props.date}
      selectedHour={props.selectedHour}
      startOptions={Object.keys(props.bookables)}
      endOptions={props.bookables[props.selectedHour]}
      onHourSelect={(hour) => props.onHourSelect(props.date, hour)}
    />
  );

  return (
    <>
      <h1 className="day__title">{dateDisplay}</h1>
      <div className="day">
        {Object.keys(props.attendance).map((hour) => (
          <Hour
            key={hour}
            hour={hour}
            attendance={props.attendance[hour]}
            selected={props.selectedHour == hour}
            onClick={() => props.onHourSelect(props.date, hour)}
          />
        ))}
      </div>
      {bookingForm}
    </>
  );
}

export default Day;
