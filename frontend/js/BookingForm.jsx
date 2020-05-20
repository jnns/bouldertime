import React from "react";
import DjangoCSRFToken from "django-react-csrftoken";
import PhoneNumberInput from "./PhoneNumberInput";

function BookingForm(props) {
  const startOptions = props.startOptions.map((hour) => (
    <option key={hour} value={hour}>
      {hour}:00
    </option>
  ));
  const endOptions = props.endOptions.map((hour) => (
    <option key={hour} value={hour}>
      {hour}:00
    </option>
  ));
  return (
    <form method="post" className="booking-form">
      <DjangoCSRFToken />
      <input type="hidden" name="date" value={props.selectedDate} />
      <select
        required
        name="start"
        value={props.selectedHour}
        onChange={(e) => props.onHourSelect(e.target.value)}
      >
        {startOptions}
      </select>
      &nbsp;&mdash;&nbsp;
      <select
        required
        name="end"
        defaultValue={props.endOptions[0]}
        disabled={Boolean(!endOptions.length)}
      >
        {endOptions}
      </select>
      <p>
        <label>
          Your cell phone number: <PhoneNumberInput />
        </label>
      </p>
      <p>
        <input type="submit" value="Request booking code" />
      </p>
    </form>
  );
}

export default BookingForm;
