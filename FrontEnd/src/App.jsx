import React, { useState,useEffect } from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import { Login } from './Pages/Login';
import { Register } from './Pages/Register';


const App = () => {
  return (
    <Router>
      <Routes>
            <Route path='/Login' element={<Login />} />
            <Route path='/Register' element={<Register />} />
            <Route path='*' element={<Login />} />
        </Routes>
    </Router>
  );
};

export default App;
