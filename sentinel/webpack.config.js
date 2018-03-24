var path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  context: __dirname,

  entry: ['./assets/js/index'],

  output: {
      path: path.resolve('./assets/bundles/'),
      filename: '[name].js',
  },

  module: {
    loaders: [
      { 
      	test: /\.jsx?$/,
      	exclude: /node_modules/,
      	loader: 'babel-loader',
     	}, // to transform JSX into JS
    ],
  },

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'})
  ],

  resolve: {
    extensions: ['.js', '.jsx']
  }
};
