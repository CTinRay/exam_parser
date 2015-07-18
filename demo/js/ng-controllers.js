
'use strict';

var requestURL = "./data/exam_test.json";

var demoApp = angular.module('demoApp', ['ngSanitize'] );



demoApp.controller( 'mainController',
	function ($scope, $http){

		var updateExamModel = function(){
			$http.get( requestURL ).
				success(function(data, status, headers, config) {
				    $scope.exam = data;
				    $scope.questions = data[0].questions;
				}).
				error(function(data, status, headers, config) {
					$scope.events = [];
				});
		};

		updateExamModel( );
	}
	
);

