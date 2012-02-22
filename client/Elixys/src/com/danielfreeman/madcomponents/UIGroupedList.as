/**
 * <p>Original Author: Daniel Freeman</p>
 *
 * <p>Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:</p>
 *
 * <p>The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.</p>
 *
 * <p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.</p>
 *
 * <p>Licensed under The MIT License</p>
 * <p>Redistributions of files must retain the above copyright notice.</p>
 */

package com.danielfreeman.madcomponents {
	
	import flash.display.DisplayObject;
	import flash.display.GradientType;
	import flash.display.Graphics;
	import flash.display.Shape;
	import flash.display.SpreadMethod;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.geom.Matrix;
	import flash.text.TextField;
	import flash.text.TextFormat;
	import flash.utils.getDefinitionByName;
	
/**
 * A heading (or an area outside a list row) was clicked
 */
	[Event( name="headingClicked", type="flash.events.Event" )]
	

/**
 *  MadComponents Grouped List
 * <pre>
 * &lt;groupedList
 *    id = "IDENTIFIER"
 *    colour = "#rrggbb"
 *    background = "#rrggbb, #rrggbb, ..."
 *    visible = "true|false"
 *    gapV = "NUMBER"
 *    gapH = "NUMBER"
 *    border = "true|false"
 *    lines = "i,j,k..."
 *    pullDownRefresh = "true|false"
 *    pullDownColour = "#rrggbb"
 *    sortBy = "IDENTIFIER"
 *    mask = "true|false"
 *    alignV = "scroll|no scroll"
 * /&gt;
 * </pre>
 */
	public class UIGroupedList extends UIList {
		
		public static const HEADING_CLICKED:String="headingClicked";
		protected static const STRIPE_WIDTH:Number = 8.0;
		protected static const PADDING:Number = 10.0;
		protected static const CELL_COLOUR:uint = 0xFFFFFF;
		protected static const CURVE:Number = 8.0;
		protected static const BLACK:TextFormat = new TextFormat("Tahoma",17,0x555566);
		protected static const WHITE:TextFormat = new TextFormat("Tahoma",17,0xFCFCFC);
		
		public static var HEADING:Class = null;
		
		protected var _cellWidth:Number;
		protected var _length:Number;
		protected var _groupPositions:Array;
		protected var _group:int = -1;
		protected var _heading:* = null;
		protected var _hasHeadings:Boolean = false;
		protected var _groupDetails:Object;
		protected var _headingFormat:TextFormat = BLACK;
		
		
		public function UIGroupedList(screen:Sprite, xml:XML, attributes:Attributes) {
			super(screen, xml, attributes);
			_field = "";
		}
		
/**
 *  Draw background
 */
		override protected function drawBackground():void {
			graphics.clear();
			if (_colours && _colours.length>0) {
				var matr:Matrix=new Matrix();
				matr.createGradientBox(STRIPE_WIDTH,_attributes.height, 0, 0, 0);
				var colour:uint = _colours[0];
				graphics.beginGradientFill(GradientType.LINEAR,[colour,Colour.lighten(colour),Colour.lighten(colour,40)], [1.0,1.0,1.0], [0x00,0x33,0xff], matr,SpreadMethod.REPEAT);
			}
			else {
				graphics.beginFill(0,0);
			}
			graphics.drawRect(0, 0, _attributes.width, _attributes.height);
		}
		
/**
 *  Assign to list by passing an array of objects
 */
		override public function set data(value:Object):void {
			_filteredData = noHeadings(_data = value as Array);
			initDrawGroups();
			clearCellGroups();
			_cellLeft = _attributes.x + _attributes.paddingH - PADDING;
			_cellWidth = _attributes.width - 2 * _attributes.paddingH + 2 * PADDING;
			_cellTop =  _top + 4 * _attributes.paddingV; //_attributes.y +
			_groupPositions = [];
			var g:int = 0;
			for each(var group:* in value) {
				if (!(group is Array)) {
					_heading = group;
				}
				else {
					_suffix = "_"+g.toString();
					_length = group.length;
					_groupDetails = {top:_cellTop, length:_length, bottom:0, cellHeight:0};
					super.data0 = group;
					_groupDetails.cellHeight = (_cellTop - _groupDetails.top) / _length;
					_groupDetails.bottom = _cellTop;
					_groupPositions.push(_groupDetails);
					_cellTop+= 4 * _attributes.paddingV;
					g++;
				}
			}
		}
		
/**
 *  Returns the data array of ojects without the headings
 */
		protected function noHeadings(value:Array):Array {
			var result:Array = [];
			for each (var group:* in value) {
				if (group is Array)
					result.push(group);
			}
			return result;
		}
		
/**
 *  Returns the data object for the last row clicked
 */
		override public function get row():Object {
			return (_group>=0 && _pressedCell>=0 && _filteredData && _filteredData[_group]) ? _filteredData[_group][_pressedCell] : null;
		}
		
/**
 *  Redraw cell chrome
 */
		override protected function redrawCells():void {
			_cellLeft = _attributes.x + _attributes.paddingH - PADDING;
			_cellWidth = _attributes.width - 2 * _attributes.paddingH + 2 * PADDING;
			_group = 0;
			for each(var groupDetails:Object in _groupPositions) {
				_length = groupDetails.length;
				_cellTop = groupDetails.top;
				initDraw();
				for (var i:int=0; i<_length; i++) {
					drawCell(_cellTop + groupDetails.cellHeight, i);
				}
			}
		}
		
/**
 *  Draw group heading
 */
		override protected function initDraw():void {
			if (_heading) {
				var heading:DisplayObject;
				var top:Number = _cellTop - 2 * _attributes.paddingV;
				if (_heading is String) {
					new UILabel(_slider, _attributes.paddingH-1, top+_attributes.paddingV / 2+1, _heading, WHITE);
					heading = new UILabel(_slider, _attributes.paddingH, top+_attributes.paddingV / 2, _heading, _headingFormat);
				}
				else if (_heading is Class) {
					_slider.addChild(heading = new _heading());
				}
				else {
					_slider.addChild(heading = _heading);
				}
				heading.x = _attributes.paddingH;
				heading.y = top + _attributes.paddingV / 2 + 1;
				_heading = null;
				_cellTop = heading.y+heading.height + _attributes.paddingV;
				_groupDetails.top = _cellTop;
			}
		}
		
		
		override protected function clearCells():void {
		}
		
		
		protected function clearCellGroups():void {
			super.clearCells();
			_cellTop = 0;
		}
		
		
		protected function initDrawGroups():void {
			_slider.graphics.clear();
			resizeRefresh();
			_slider.graphics.beginFill(0,0);
			_slider.graphics.drawRect(0,-4*_attributes.paddingV-(_refresh ? TOP : 0),1,1);
		}
		
/**
 *  Rearrange the layout to new screen dimensions
 */	
		override public function layout(attributes:Attributes):void {
			initDrawGroups();
			super.layout(attributes);
		}
		
/**
 *  Draw the background for a cell somewhere in the middle of a group
 */	
		override protected function drawCell(position:Number, count:int):void {
			_slider.graphics.beginFill(_colour);
			var colour:uint = CELL_COLOUR;
			if (_colours.length > 1)
				colour = _colours[Math.min(_colours.length - 1, count + 1)];
			if (_length==1) {	
				_slider.graphics.drawRoundRect(_cellLeft, _cellTop, _cellWidth + 1, position - _cellTop, 1.5 * CURVE);
				_slider.graphics.beginFill(colour);
				_slider.graphics.drawRoundRect(_cellLeft + 1, _cellTop + 1, _cellWidth - 1, position - _cellTop - 2, 1.5 * CURVE);
			}
			else if (count==0) {
				curvedTop(_slider.graphics, _cellLeft, _cellTop, _cellLeft + _cellWidth + 1, position);
				_slider.graphics.beginFill(colour);
				curvedTop(_slider.graphics, _cellLeft + 1, _cellTop + 1, _cellLeft + _cellWidth, position);
			}
			else if (count==_length-1) {
				curvedBottom(_slider.graphics, _cellLeft, _cellTop, _cellLeft + _cellWidth + 1, position);
				_slider.graphics.beginFill(colour);
				curvedBottom(_slider.graphics, _cellLeft + 1, _cellTop + 1, _cellLeft + _cellWidth, position - 1);
			}
			else {
				_slider.graphics.drawRect(_cellLeft, _cellTop, _cellWidth + 1, position - _cellTop);
				_slider.graphics.beginFill(colour);
				_slider.graphics.drawRect(_cellLeft + 1, _cellTop + 1, _cellWidth - 1, position - _cellTop);
			}
			drawLines(position);
			_cellTop = position;
		}
		
/**
 *  Draw the background of the top cell of a group
 */	
		public static function curvedTop(shape:Graphics, left:Number, top:Number, right:Number, bottom:Number):void {
			shape.moveTo(left + CURVE, top);
			shape.lineTo(right - CURVE, top);
			shape.curveTo(right, top, right, top + CURVE);
			shape.lineTo(right, bottom);
			shape.lineTo(left, bottom);
			shape.lineTo(left, top + CURVE);
			shape.curveTo(left, top, left + CURVE, top);
		}
		
/**
 *  Draw the background of the bottom cell of a group
 */
		public static function curvedBottom(shape:Graphics, left:Number, top:Number, right:Number, bottom:Number):void {
			shape.moveTo(left, top);
			shape.lineTo(right, top);
			shape.lineTo(right, bottom - CURVE);
			shape.curveTo(right, bottom, right - CURVE, bottom);
			shape.lineTo(left + CURVE, bottom);
			shape.curveTo(left, bottom, left, bottom - CURVE);
			shape.lineTo(left, top);		
		}
		
/**
 *  Is a group row clicked?
 */
		protected function isPressButton():Boolean {
			_group = 0;
			for each(var detail:Object in _groupPositions) {
				if (_slider.mouseY >= detail.top && _slider.mouseY <= detail.bottom) {
					_pressedCell = Math.floor((_slider.mouseY - detail.top) / detail.cellHeight);
					return true;
				}
				else if (_slider.mouseY <= detail.bottom) {
					return false;
				}
				_group++;
			}
			return false;
		}
		
/**
 *  The last group clicked
 */
		public function get group():int {
			return _group;
		}
		
/**
 *  Group heading text colour
 */
		public function set headingColour(value:uint):void {
			_headingFormat.color = value;
		}
		
/**
 *  Scroll to this position in the list
 */
		override public function set index(value:int):void {
			_pressedCell = value;
			_slider.y = - _groupPositions[_group].cellHeight * value - _groupPositions[_group].top;
		}
		
/**
 *  Assign to group before assigning to index
 */
		public function set group(value:int):void {
			_group = value;
		}
		
/**
 *  Return DisplyObject of button pressed
 */
		override protected function pressButton():DisplayObject {
			_scrollBarLayer.graphics.clear();
			if (!_simple  || _slider.mouseY<_top) {
				doSearchHit();
			}
			if (!_pressButton && _clickRow) {
				if (isPressButton()) {
					drawHighlight();
					activate();
				}
				else if (_slider.mouseY > _top) {
					dispatchEvent(new Event(HEADING_CLICKED));
				}
			}
			return _pressButton;
		}
		
/**
 *  Return row matching group and row indexes
 */
		protected function byGroupAndRow(group:uint,row:uint):DisplayObject {
			return _slider.getChildByName("label_"+row.toString()+"_"+group.toString());
		}
		
/**
 *  Return component matching id within row matching group and row indexes
 */
		override public function findViewById(id:String, row:int = -1, group:int = -1):DisplayObject {
			if (_search && _search.name == id) {
				return _search;
			}
			else {
				var container:DisplayObject = byGroupAndRow(group,row);
				return (container && container is UIForm) ? UIForm(container).findViewById(id, row, group) : container;
			}
		}

/**
 *  Set XML data
 */
		override public function set xmlData(value:XML):void {
			var result:Array = [];
			var children:XMLList = value.group;
			for each (var group:XML in children) {
				var row:Array = [];
				if (group.@icon.length()>0)
					result.push(getDefinitionByName(group.@icon.toString()) as Class);
				else if (group.@label.length()>0)
					result.push(group.@label.toString());
				for each (var child:XML in group.children()) {
					var item:Object = {label:((child.@label.length()>0) ? child.@label : child.localName())};
					row.push(item);
				}
				result.push(row);
			}
			data = result;
		}
		
/**
 *  Draw highlight when a row is clicked
 */
		protected function drawHighlight():void {
			var groupDetails:Object = _groupPositions[_group];
			var length:int = groupDetails.length;
			var top:Number = groupDetails.top + _pressedCell * groupDetails.cellHeight;
			var bottom:Number = top + groupDetails.cellHeight;
			_highlight.graphics.beginFill(HIGHLIGHT);
			if (length==1) {
				_highlight.graphics.drawRoundRect(_cellLeft, top, _cellWidth, bottom - top, 1.5 * CURVE);
			}
			else if (_pressedCell==0) {
				curvedTop(_highlight.graphics, _cellLeft, top, _cellLeft + _cellWidth, bottom);
			}
			else if (_pressedCell==length-1) {
				curvedBottom(_highlight.graphics, _cellLeft, top, _cellLeft + _cellWidth, bottom);
			}
			else {
				_highlight.graphics.drawRect(_cellLeft, top, _cellWidth + 1, bottom - top);
			}
		}
		
		
		override protected function searchHandler(event:Event):void {
		}
		
	}
}