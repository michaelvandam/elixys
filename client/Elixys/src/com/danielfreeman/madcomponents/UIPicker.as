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

package com.danielfreeman.madcomponents
{
	import flash.display.DisplayObject;
	import flash.display.GradientType;
	import flash.display.Shape;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.geom.Matrix;
	
/**
 *  MadComponents picker component
 * <pre>
 * &lt;picker
 *    id = "IDENTIFIER"
 *    colour = "#rrggbb"
 *    background = "#rrggbb, #rrggbb, ..."
 *    visible = "true|false"
 *    gapV = "NUMBER"
 *    gapH = "NUMBER"
 *    border = "true|false"
 *    lines = "i,j,k..."
 *    sortBy = "IDENTIFIER"
 *    index = "INTEGER"
 *    height = "NUMBER"
 *    cursorheight = "NUMBER"
 * /&gt;
 * </pre>
 */
	public class UIPicker extends UIList
	{	
		protected static const HEIGHT:Number = 160.0;
		protected static const SPINNER_ALPHA:Number = 1.0;
		protected static const SPINNER_SHADE:Number = 0x30;
		protected static const SPINNER_CURSOR_HEIGHT:Number = 60.0;
		protected static const SPINNER_CURSOR_COLOUR:uint = 0x666699;
		protected static const SPINNER_CURSOR_COLOUR_DARK:uint = 0x333399;
		protected static const SPINNER_CURSOR_COLOUR_HIGHLIGHT:uint = 0xCCCCFF;
		protected static const SPINNER_CURSOR_ALPHA:Number = 0.3;
		protected static const CURVE:Number = 10.0;
		protected static const WARP:Number = 3.0;
		protected static const SHADOW:Number = 10.0;
		
		public static var PICKER_DECAY:Number = 0.98;
		
		protected var _spinner:Shape=null;
		protected var _mask:Shape=null;
		protected var _spinnerColour:uint = 0x333333;
		protected var _left:Boolean;
		protected var _right:Boolean;
		protected var _pickerHeight:Number = HEIGHT;
		protected var _cursorHeight:Number = SPINNER_CURSOR_HEIGHT;
		
		public function UIPicker(screen:Sprite, xml:XML, attributes:Attributes, left:Boolean =false, right:Boolean = false, pickerHeight:Number = -1, cursorHeight:Number = -1) {
			if (pickerHeight>0)
				_pickerHeight = pickerHeight;
			if (cursorHeight>0)
				_cursorHeight = cursorHeight;
			if (xml.@height.length()>0)
				_pickerHeight = parseFloat(xml.@height[0]);
			if (xml.@cursorHeight.length()>0)
				_cursorHeight = parseFloat(xml.@cursorHeight[0]);
			super(screen, xml, attributes);
			_decay = PICKER_DECAY;
			_deltaThreshold = 4.0;
			_mask = new Shape();
			_spinner = new Shape();
			_left = left;
			_right = right;
			drawSpinner();
			addChild(_spinner);
			addChild(this.mask = _mask);
		}

/**
 *  Draw picker chrome
 */
		protected function drawSpinner():void {
			var matr:Matrix=new Matrix();
			
			_mask.graphics.clear();
			_mask.graphics.beginFill(0);
			drawShape(_mask);
			
			_mask.visible = false;
			
			_spinner.graphics.clear();
			
			matr.createGradientBox(_attributes.width, _pickerHeight, Math.PI/2, 0, 0);
			_spinner.graphics.beginGradientFill(GradientType.LINEAR, [_spinnerColour,_spinnerColour,_spinnerColour, _spinnerColour, _spinnerColour,_spinnerColour], [SPINNER_ALPHA,0.2,0.0,0.0,0.2,SPINNER_ALPHA], [0x00,SPINNER_SHADE/2,SPINNER_SHADE,0xff-SPINNER_SHADE,0xff-SPINNER_SHADE/2,0xff], matr);
			_spinner.graphics.lineStyle(1.5,0x333333,1.0,true);
			drawShape(_spinner);
			_spinner.graphics.lineStyle(0,0,0);
			
			_spinner.graphics.beginGradientFill(GradientType.LINEAR, [0x000000,0xDDDDDD,0xDDDDDD,0x000000], [1.0,1.0,1.0,1.0], [0x00,SPINNER_SHADE,0xff-SPINNER_SHADE,0xff], matr);
			_spinner.graphics.drawRect(1, 0, 3, _pickerHeight);
			_spinner.graphics.drawRect(_attributes.width-3, 0, 3, _pickerHeight);
			
			matr.createGradientBox(_attributes.width, _cursorHeight / 2, Math.PI/2, 0, (_pickerHeight - _cursorHeight)/2);
			_spinner.graphics.beginGradientFill(GradientType.LINEAR, [SPINNER_CURSOR_COLOUR_HIGHLIGHT,SPINNER_CURSOR_COLOUR], [SPINNER_CURSOR_ALPHA,SPINNER_CURSOR_ALPHA], [0x00,0xff], matr);
			_spinner.graphics.drawRect(0, (_pickerHeight - _cursorHeight)/2, _attributes.width, _cursorHeight / 2);
			
			_spinner.graphics.beginFill( SPINNER_CURSOR_COLOUR_DARK, SPINNER_CURSOR_ALPHA );
			_spinner.graphics.drawRect(0, _pickerHeight / 2, _attributes.width, _cursorHeight / 2);
			
			_spinner.graphics.beginFill(SPINNER_CURSOR_COLOUR);
			_spinner.graphics.drawRect(0, (_pickerHeight - _cursorHeight)/2, _attributes.width, 1.5);
			_spinner.graphics.drawRect(0, (_pickerHeight + _cursorHeight)/2-1, _attributes.width, 1.5);
			
			
			matr.createGradientBox(_attributes.width, SHADOW, Math.PI/2, 0, (_pickerHeight + _cursorHeight)/2);
			_spinner.graphics.beginGradientFill(GradientType.LINEAR, [_spinnerColour,_spinnerColour], [SPINNER_ALPHA/3,0.0], [0x00,0xff], matr);
			_spinner.graphics.drawRect(0, (_pickerHeight + _cursorHeight)/2, _attributes.width, _cursorHeight / 2);

		}
		
/**
 *  Basic picker shape
 */
		protected function drawShape(spinner:Shape):void {
			spinner.graphics.moveTo(_left ? (CURVE + 2*WARP): 0,0);
			spinner.graphics.lineTo(_attributes.width-(_right ? (CURVE + 2 * WARP) : 0),0);
			if (_right) {
				spinner.graphics.curveTo(_attributes.width - 2*WARP,0,_attributes.width-WARP,CURVE);
				spinner.graphics.curveTo(_attributes.width + WARP,_pickerHeight/2,_attributes.width-WARP,_pickerHeight-1-CURVE);
			}
			else {
				spinner.graphics.lineTo(_attributes.width,_pickerHeight-1);
			}
			if (_right) {
				spinner.graphics.curveTo(_attributes.width-2*WARP,_pickerHeight-1,_attributes.width-CURVE-2*WARP,_pickerHeight-1);
			}
			spinner.graphics.lineTo((_left ? CURVE+2*WARP : 0),_pickerHeight-1);
			if (_left) {
				spinner.graphics.curveTo(WARP,_pickerHeight-1,WARP,_pickerHeight-1-CURVE);
				spinner.graphics.curveTo(-WARP,_pickerHeight/2,WARP,CURVE);
			}
			else {
				spinner.graphics.lineTo(0,0);
			}
			if (_left) {
				spinner.graphics.curveTo(WARP,0,CURVE+2*WARP,0);
			}
		}
		

		override public function get height():Number {
			return _pickerHeight;
		}

/**
 *  Rearrange the layout to new screen dimensions
 */	
		override public function layout(attributes:Attributes):void {
			super.layout(attributes);
			if (_spinner)
				drawSpinner();
		}
		
		
		override protected function startMovement0():Boolean {
			if (_slider.y > _offset) {
				_endSlider = -_offset;
				return true;
			}
			else if (_slider.y < -(_cellHeight * (_count - 3) - _offset)) {
				_endSlider = _cellHeight * (_count - 3) - _offset;
				return true;
			}

			return false;
		}
		
		
/**
 *  Data object for last row clicked
 */
		override public function get row():Object {
			return (_pressedCell>=0) ? _filteredData[_pressedCell+1] : null;
		}
		
		
		override protected function pressButton():DisplayObject {
			return null;
		}
		
		
		override protected function showScrollBar():void {
		}
		
		
		override protected function stopMovement():void {
			if (_slider.y < _offset && _slider.y > -(_cellHeight * (_count - 3) - _offset)) {
				_endSlider = - _cellHeight * Math.round((_slider.y-_offset)/_cellHeight) - _offset;
				_delta = (-_endSlider - _slider.y) * BOUNCE;
				if (Math.abs(_slider.y+_endSlider) < 1.0) {
					stopMovement0();
				}
			}
			else {
				stopMovement0();
			}
		}
		
		
		protected function stopMovement0():void {
			_moveTimer.stop();
			hideScrollBar();
			_pressedCell=-Math.round((_slider.y-_offset)/_cellHeight);
			dispatchEvent(new Event(Event.CHANGE));
		}
		
/**
 *  Draw picker background
 */	
		override protected function drawBackground():void {
			if (_colours && _colours.length>0) {
				graphics.beginFill(_colours[0]);
			}
			else {
				graphics.beginFill(0xFFFFFF);
			}
			graphics.drawRect(0, 0, _attributes.width, _attributes.height);
		}
		
/**
 *  Set array of objects data
 */	
		override public function set data(value:Object):void {
			value.splice(0,0,{label:" "});
			value.push({label:" "});
			super.data = value;
			_offset = (_pickerHeight - _cellHeight * (Math.floor(_pickerHeight/_cellHeight) + 1)) / 2;
			_offset += _cellHeight * (Math.floor(_pickerHeight/(2*_cellHeight))-1);
			if (Math.floor(_pickerHeight/_cellHeight) % 2 ==1)
				_offset +=_cellHeight/2;
			_slider.y = _offset;
			if (_spinner)
				setChildIndex(_spinner, numChildren-1);
		}

	}
}