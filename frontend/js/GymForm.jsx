import React from "react";

class GymForm extends React.Component {
  constructor(props) {
    this.handleChange = this.handleChange.bind(this);
  }
  handleChange(e) {
    const gymName = e.target.value;
    document.href = `/g/${gymName}/`;
  }
  render() {
    <select
      name="gym"
      defaultValue={this.props.gym}
      onChange={this.handleChange}
    >
      {this.props.options.map((name, slug) => (
        <option value={slug}>{name}</option>
      ))}
    </select>;
  }
}

export default GymForm;
