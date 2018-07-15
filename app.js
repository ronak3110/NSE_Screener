'use strict';
var app = angular.module('mainApp', []);

var stockService = app.service('stockService', function ($http) {
  this.getNiftyStocks = function (callbackFunc) {
    $http({
      method: "GET",
      url: "http://127.0.0.1:5002/niftyStocks"
    }).then(function mySuccess(response) {
      console.log(response.data);
      callbackFunc(response.data);
    }, function myError(response) {
    });
  };

  this.updateData = function (callbackFunc) {
    $http({
      method: "GET",
      url: "http://127.0.0.1:5002/refreshData"
    }).then(function mySuccess(response) {
      callbackFunc();
    }, function myError(response) {
    });
  }

  this.shutdown = function () {
    $http({
      method: "GET",
      url: "http://127.0.0.1:5002/terminate"
    }).then(function mySuccess(response) {
      alert("Server Shutdown complete");
    }, function myError(response) {
    });
  }
  
  this.setSchedulerTime = function(newTime){
    $http({
      method: "GET",
      url: "http://127.0.0.1:5002/updateTime?time="+newTime
    }).then(function mySuccess(response) {
      alert("updated scheduler timer");
    }, function myError(response) {
    });
  };

  this.getMidCapStocks = function (callbackFunc) {
    $http({
      method: "GET",
      url: "http://127.0.0.1:5002/midcapNiftyStocks"
    }).then(function mySuccess(response) {
      console.log(response.data);
      callbackFunc(response.data);
    }, function myError(response) {
    });
  };

  this.getNextNiftyStocks = function (callbackFunc) {
    $http({
      method: "GET",
      url: "http://127.0.0.1:5002/NextNiftyStocks"
    }).then(function mySuccess(response) {
      console.log(response.data);
      callbackFunc(response.data);
    }, function myError(response) {
    });
  };

});
app.controller('stockController', function ($scope, stockService, $http) {
  var gridDiv = document.querySelector('#myGrid');
  $scope.selectedTab = "Nifty 50";
  $scope.midcapNiftyStocks = [];
  $scope.niftyStocks = [];
  $scope.nextNiftyStocks = [];
  $scope.rowData = [];
  var columnDefs = [
    { headerName: "Symbol", field: "symbol" },
    { headerName: "Open", field: "open" },
    { headerName: "Low", field: "low" },
    { headerName: "High", field: "high" },
    { headerName: "Trade Volume", field: "trdVol" },
    { headerName: "Open-Low", field: "openLow" },
    { headerName: "openlowStatus", field: "openLowStatus" },
    { headerName: "Open-high", field: "openHigh" },
    { headerName: "openhighStatus", field: "openHighStatus" }
  ];

  function createNewEntry(symbol, open, low, high, trdVol) {
    var item = {
      symbol: symbol,
      open: open,
      low: low,
      high: high,
      trdVol: trdVol,
      openLow: (open.replace(/,/g, "") - low.replace(/,/g, "")).toFixed(2),
      openLowStatus: open.replace(/,/g, "") - low.replace(/,/g, "") === 0 ? "BUY" : "",
      openHigh: (open.replace(/,/g, "") - high.replace(/,/g, "")).toFixed(2),
      openHighStatus: open.replace(/,/g, "") - high.replace(/,/g, "") === 0 ? "SELL" : "",
    };
    return item;
  }
  $scope.gridOptions = {
    animateRows: true,
    columnDefs: columnDefs,
    rowData: $scope.rowData,
    enableFilter: true,
    floatingFilter: true,
    getRowStyle: getRowStyleScheduled,
    enableSorting: true,
    onGridReady: function () {
      sizeToFit();
    }
  };

  function sizeToFit() {
    $scope.gridOptions.api.sizeColumnsToFit();
  };

  $scope.getNiftyStocks = function () {
    $scope.selectedTab = "Nifty 50";
    $scope.gridOptions.api.setRowData([])
    stockService.getNiftyStocks(function (data) {
      console.log(data);
      for (var i = 0; i < data.data.length; i++) {
        var newItem = createNewEntry(data.data[i].symbol, data.data[i].open, data.data[i].low, data.data[i].high, data.data[i].trdVol);
        var res = $scope.gridOptions.api.updateRowData({ add: [newItem] });
      }
      sizeToFit();
    });
  };

  $scope.getNextNiftyStocks = function () {
    $scope.selectedTab = "Nifty Next 50";
    $scope.gridOptions.api.setRowData([]);
    stockService.getNextNiftyStocks(function (data) {
      console.log(data);
      for (var i = 0; i < data.data.length; i++) {
        var newItem = createNewEntry(data.data[i].symbol, data.data[i].open, data.data[i].low, data.data[i].high, data.data[i].trdVol);
        var res = $scope.gridOptions.api.updateRowData({ add: [newItem] });
      }
      sizeToFit();
    });
  };

  $scope.update = function () {
    $scope.gridOptions.api.showLoadingOverlay();
    stockService.updateData(function () {
      switch ($scope.selectedTab) {
        case 'Nifty 50': $scope.getNiftyStocks();
          break;
        case 'Nifty Next 50': $scope.getNextNiftyStocks();
          break;
        case 'Nifty MidCap 50': $scope.getMidCapNiftyStocks();
      }
      $scope.gridOptions.api.hideOverlay();
    });
  };

  $scope.getMidCapNiftyStocks = function () {
    $scope.selectedTab = "Nifty MidCap 50";
    $scope.gridOptions.api.setRowData([]);
    stockService.getMidCapStocks(function (data) {
      console.log(data);
      for (var i = 0; i < data.data.length; i++) {
        var newItem = createNewEntry(data.data[i].symbol, data.data[i].open, data.data[i].low, data.data[i].high, data.data[i].trdVol);
        var res = $scope.gridOptions.api.updateRowData({ add: [newItem] });
      }
      sizeToFit();
    });
  };

  $scope.terminate = function () {
    stockService.shutdown();
    alert("Server Shutdown complete");
  };

  $scope.init = function () {
    new agGrid.Grid(gridDiv, $scope.gridOptions);
    stockService.getNiftyStocks(function (data) {
      $scope.gridOptions.api.setRowData([]);
      console.log(data.data);
      for (var i = 0; i < data.data.length; i++) {
        var newItem = createNewEntry(data.data[i].symbol, data.data[i].open, data.data[i].low, data.data[i].high, data.data[i].trdVol);
        var res = $scope.gridOptions.api.updateRowData({ add: [newItem] });
      }
      sizeToFit();
    });
  };
  $scope.setSchedulerTime = function(){
    if($scope.schedulerTime !== "undefined"){
      stockService.setSchedulerTime($scope.schedulerTime);
    }else{
      alert("enter the time in proper format (hh:mm) ex. (09:25) or (15:30)");
    }
  };

  function getRowStyleScheduled(params) {
    if (params.data.openLowStatus === 'BUY') {
      return {
        'background-color': 'GREEN',
        'color': 'WHITE'
      }
    } else if (params.data.openHighStatus === 'SELL') {
      return {
        'background-color': 'RED',
        'color': 'WHITE'
      };
    }
    return null;
  };

  $scope.init();

});