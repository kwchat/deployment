import logo from './logo.svg';
import './App.css';
import React from 'react';
import ReactDOM from 'react-dom';

class Content extends React.Component {
  render() {
    return (
      <div class="content">
        <ul role="listbox">
          
        </ul>
      </div>
    )
  }
}

function App() {
  return (
    <div class="App">
      <header>
        <h1>KW Chat</h1>
      </header>
      <Content />
      <footer>
        <input type="text" />
        <button>Put</button>
      </footer>
    </div>
  );
}

export default App;
