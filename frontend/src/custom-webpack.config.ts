import { EnvironmentPlugin } from 'webpack';

const path = require('path');

const Dotenv = require('dotenv-webpack');
module.exports = {
  plugins: [new Dotenv()],
};