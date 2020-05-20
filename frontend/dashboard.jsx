import React from "react";
import ReactDOM from "react-dom";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";

import "./scss/dashboard.scss";

function formatDate(date) {
  return date.toLocaleTimeString({ hc: "h24" });
}

function shortTime(time) {
  return time.split(":").slice(0, 2).join(":");
}

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

var csrftoken = getCookie("csrftoken");

class AddButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = { displayForm: false };
  }

  render() {
    if (!this.state.displayForm) {
      return (
        <div
          className="new-guest__add-button"
          onClick={() => this.setState({ displayForm: true })}
        >
          <svg
            aria-hidden="true"
            focusable="false"
            data-prefix="fas"
            data-icon="user-plus"
            className="svg-inline--fa fa-user-plus fa-w-20"
            role="img"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 640 512"
          >
            <path
              fill="currentColor"
              d="M624 208h-64v-64c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v64h-64c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h64v64c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-64h64c8.8 0 16-7.2 16-16v-32c0-8.8-7.2-16-16-16zm-400 48c70.7 0 128-57.3 128-128S294.7 0 224 0 96 57.3 96 128s57.3 128 128 128zm89.6 32h-16.7c-22.2 10.2-46.9 16-72.9 16s-50.6-5.8-72.9-16h-16.7C60.2 288 0 348.2 0 422.4V464c0 26.5 21.5 48 48 48h352c26.5 0 48-21.5 48-48v-41.6c0-74.2-60.2-134.4-134.4-134.4z"
            ></path>
          </svg>
        </div>
      );
    } else {
      return <Form onCancel={() => this.setState({ displayForm: false })} />;
    }
  }
}

class Form extends React.Component {
  constructor(props) {
    super(props);
    this.state = { bookables: {} };
  }
  componentDidMount() {
    fetch("/api/gyms/bouldergarten/bookables/")
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        this.setState({ bookables: data });
      });
  }
  render() {
    console.log("render");
    return (
      <form className="new-guest__form">
        <label>
          From{" "}
          <select>
            {Object.keys(this.state.bookables).forEach((hour) => {
              console.log(hour);
              return (
                <option key={hour} value={hour}>
                  {hour}
                </option>
              );
            })}
          </select>
        </label>
        <label>
          To{" "}
          <select>
            <option></option>
          </select>
        </label>
        <input type="submit" value="Submit" />
        <input type="button" value="Cancel" onClick={this.props.onCancel} />
      </form>
    );
  }
}

function Booking(props) {
  const booking = props.booking;
  return (
    <Draggable draggableId={String(props.booking.id)} index={props.index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          className={
            "booking " + (snapshot.isDragging ? "booking--dragged" : "")
          }
          onDoubleClick={props.onDoubleClick}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
        >
          <span className="booking__name">{booking.name}</span>
          <div className="booking__scheduled">
            <span className="booking__start">{shortTime(booking.start)}</span>
            <span className="booking__end">{shortTime(booking.end)}</span>
          </div>
        </div>
      )}
    </Draggable>
  );
}

function ColumnHeader(props) {
  const columnName = {
    waiting: "waiting",
    checkedIn: "bouldering",
    checkedOut: "out",
  };

  return (
    <div className="column__header">
      <div className="column__name">{columnName[props.name]}</div>
    </div>
  );
}
function MainColumnHeader(props) {
  return (
    <div className="column__header">
      <div className="column__name">Bouldering</div>
      <div className="column__guests">
        {props.guests} / {props.maxGuests}
      </div>
    </div>
  );
}

class Column extends React.Component {
  getColumnHeader() {
    if (this.props.name === "checkedIn") {
      return (
        <MainColumnHeader
          name={this.props.name}
          guests={this.props.bookings.length}
          maxGuests={this.props.maxGuests}
        />
      );
    } else {
      return <ColumnHeader name={this.props.name} />;
    }
  }

  render() {
    return (
      <div className="column">
        {this.getColumnHeader()}
        <Droppable droppableId={this.props.name}>
          {(provided, snapshot) => (
            <div
              className={
                "column__bookings " +
                (snapshot.isDraggingOver
                  ? "column__bookings--is_dragged_over"
                  : "")
              }
              ref={provided.innerRef}
              {...provided.droppableProps}
            >
              {this.props.bookings.map((booking, index) => (
                <Booking
                  index={index}
                  key={booking.id}
                  onDoubleClick={() => this.props.updateBooking(booking.id)}
                  booking={booking}
                />
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </div>
    );
  }
}

class Columns extends React.Component {
  state = { waiting: [], checkedIn: [], checkedOut: [] };

  componentDidMount() {
    this.getBookings();
    setInterval(this.getBookings, 1000 * 5);
  }

  getBookings = () => {
    fetch("/api/bookings/")
      .then((response) => response.json())
      .then((data) => {
        this.setState({
          waiting: data.filter((b) => Boolean(!b.checkin_at && !b.checkout_at)),
          checkedIn: data.filter((b) =>
            Boolean(b.checkin_at && !b.checkout_at)
          ),
          checkedOut: data.filter((b) => b.checkout_at),
        });
      });
  };

  updateBooking = (id, data) => {
    fetch(`/api/bookings/${id}/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify(data),
    }).then(() => {
      this.getBookings();
    });
  };

  reset = (id) => {
    this.updateBooking(id, {
      checkin_at: null,
      checkout_at: null,
    });
  };

  checkIn = (id) => {
    this.updateBooking(id, {
      checkin_at: formatDate(new Date()),
      checkout_at: null,
    });
  };

  checkOut = (id) => {
    this.updateBooking(id, { checkout_at: formatDate(new Date()) });
  };

  onDragEnd = (result) => {
    const { destination, source, draggableId } = result;
    if (!destination) {
      return;
    }

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    destination.droppableId;
    switch (destination.droppableId) {
      case "checkedIn":
        this.checkIn(draggableId);
        break;
      case "checkedOut":
        this.checkOut(draggableId);
        break;
      case "waiting":
        this.reset(draggableId);
        break;
    }
  };

  render() {
    return (
      <>
        <DragDropContext onDragEnd={this.onDragEnd}>
          <div className="columns">
            <Column
              name="waiting"
              updateBooking={(id) => this.checkIn(id)}
              bookings={this.state.waiting}
            />
            <Column
              name="checkedIn"
              maxGuests={this.props.maxGuests}
              updateBooking={(id) => this.checkOut(id)}
              bookings={this.state.checkedIn}
            />
            <Column
              name="checkedOut"
              updateBooking={(id) => this.checkIn(id)}
              bookings={this.state.checkedOut}
            />
          </div>
        </DragDropContext>
        <AddButton />
      </>
    );
  }
}

const dashboard = document.getElementById("dashboard");
ReactDOM.render(<Columns maxGuests={dashboard.dataset.maxGuests} />, dashboard);
