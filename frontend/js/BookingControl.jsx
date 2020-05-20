import React from "react";

import Day from "./Day";

class BookingControl extends React.Component {
  state = { date: null, hour: null, endHour: null };

  render() {
    return (
      <>
        {Object.keys(this.props.attendance).map((date) => {
          return (
            <Day
              key={date}
              date={date}
              selectedHour={this.state.date === date ? this.state.hour : null}
              attendance={this.props.attendance[date]}
              bookables={this.props.bookables[date]}
              onHourSelect={(date, hour) =>
                this.setState({ date: date, hour: hour })
              }
            />
          );
        })}
      </>
    );
  }
}

export default BookingControl;
