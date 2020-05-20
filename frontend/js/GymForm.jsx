import React from "react";
import ReactDOM from "react-dom";

class GymForm extends React.Component {
  handleChange(e) {
    const gym = e.target.value;
    if (gym) {
      document.location.href = `/${gym}/`;
    }
  }
  render() {
    return (
      <select name="gym" onChange={(e) => this.handleChange(e)}>
        <option>---</option>
        {this.props.options.map((gym) => (
          <option key={gym.slug} value={gym.slug}>
            {gym.name}
          </option>
        ))}
      </select>
    );
  }
}

ReactDOM.render(
  <GymForm options={window.gyms} />,
  document.querySelector("[id=gym]")
);
