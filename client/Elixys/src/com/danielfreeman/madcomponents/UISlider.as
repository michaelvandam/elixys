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
	import flash.display.GradientType;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.geom.Matrix;
	import flash.events.Event;

/**
 * The slider value has changed
 */
	[Event( name="change", type="flash.events.Event" )]
	

/**
 *  MadComponent slider
 * <pre>
 * &lt;slider
 *   id = "IDENTIFIER"
 *   background = "#rrggbb, #rrggbb, ..."
 *   alignH = "left|right|centre|fill"
 *   alignV = "top|bottom|centre"
 *   visible = "true|false"
 *   width = "NUMBER"
 *   alt = "true|false"
 * /&gt;
 * </pre>
 */
	public class UISlider extends MadSprite
	{
		protected static const WIDTH:Number = 120.0;
		protected static const RADIUS:Number = 12.0;
		protected static const KNOB_COLOUR:uint = 0xDDDDDD;
		protected static const HIGHLIGHT_COLOUR:uint = 0x3333CC;
		protected static const SLIDER_COLOUR:uint = 0xAAAAAA;
		protected static const SLIDER_HEIGHT:Number = 8.0;
		
		protected var _knob:Sprite;
		protected var _sliderColour:uint;
		protected var _highlightColour:uint;
		protected var _knobColour:uint;
		protected var _width:Number = WIDTH;
		protected var _value:Number = 0.5;
		
		public function UISlider(screen:Sprite, xx:Number, yy:Number, colours:Vector.<uint> = null) {
			screen.addChild(this);
			x=xx; y=yy;

			if (!colours)
				colours = new <uint>[];
			
			_highlightColour = (colours.length>0) ? colours[0] : HIGHLIGHT_COLOUR
			_knobColour = (colours.length>1) ? colours[1] : KNOB_COLOUR;
			_sliderColour = (colours.length>2) ? colours[2] : SLIDER_COLOUR;

			drawKnob();
			value = _value;
			_knob.addEventListener(MouseEvent.MOUSE_DOWN, mouseDown);
			_knob.buttonMode = _knob.useHandCursor = true;
		}
		
		
		protected function mouseDown(event:MouseEvent):void {
			stage.addEventListener(MouseEvent.MOUSE_MOVE, mouseMove);
			stage.addEventListener(MouseEvent.MOUSE_UP, mouseUp);
		}
		
		
		protected function mouseMove(event:MouseEvent):void {
			_knob.x = mouseX;
			if (_knob.x < RADIUS)
				_knob.x = RADIUS;
			else if (_knob.x > _width - RADIUS)
				_knob.x = _width - RADIUS;
			_value = (_knob.x - RADIUS) / (_width - 2*RADIUS);
			drawSlider();
			dispatchEvent(new Event(Event.CHANGE));
		}
		
		
		protected function mouseUp(event:MouseEvent):void {
			stage.removeEventListener(MouseEvent.MOUSE_MOVE, mouseMove);
			stage.removeEventListener(MouseEvent.MOUSE_UP, mouseUp);
			dispatchEvent(new Event(Event.COMPLETE));
		}
		
		
		protected function drawKnob():void {
			addChild(_knob=new Sprite());
			var matr:Matrix = new Matrix();
			matr.createGradientBox(RADIUS*2, RADIUS*2, Math.PI/2, 0, -RADIUS);
			_knob.graphics.beginFill(Colour.darken(_knobColour));
			_knob.graphics.drawCircle(0.3, 0.3, RADIUS+1);
			_knob.graphics.beginGradientFill(GradientType.LINEAR, [Colour.lighten(_knobColour),Colour.darken(_knobColour)], [1.0,1.0], [0x00,0xff], matr);
			_knob.graphics.drawCircle(0, 0, RADIUS);
			_knob.graphics.beginGradientFill(GradientType.LINEAR, [Colour.darken(_knobColour),_knobColour,Colour.lighten(_knobColour,32)], [1.0,1.0,1.0], [0x00,0x66,0xFF], matr);
			_knob.graphics.drawCircle(0, 0, RADIUS-1);
			_knob.y = RADIUS;
			_knob.buttonMode = _knob.useHandCursor = true;
		}
		
		
		protected function drawSlider():void {
			var matr:Matrix = new Matrix();
			matr.createGradientBox(_width, SLIDER_HEIGHT, Math.PI/2, 0, RADIUS - SLIDER_HEIGHT/2);
			graphics.clear();
			graphics.beginGradientFill(GradientType.LINEAR, [Colour.darken(_sliderColour,-64),_sliderColour,Colour.lighten(_sliderColour,64),Colour.lighten(_sliderColour,64)], [1.0,1.0,1.0,1.0], [0x00,0x00,0x80,0xff], matr);
			graphics.drawRoundRect(0, RADIUS - SLIDER_HEIGHT/2, _width, SLIDER_HEIGHT, SLIDER_HEIGHT);
			graphics.beginGradientFill(GradientType.LINEAR, [Colour.darken(_highlightColour,-64),_highlightColour,Colour.lighten(_highlightColour,64),Colour.lighten(_highlightColour,64)], [1.0,1.0,1.0,1.0], [0x00,0x00,0x80,0xff], matr);
			graphics.drawRoundRect(0, RADIUS - SLIDER_HEIGHT/2, _width * _value, SLIDER_HEIGHT, SLIDER_HEIGHT);
		}
		
/**
 *  Set value of slider, between "0" and "1"
 */
		public function set text(txt:String):void {
			value = Number(txt);
		}
		
/**
 *  Set value of slider, a number between 0 and 1
 */
		public function set value(valuu:Number):void {
			_value = valuu;
			_knob.x = RADIUS + valuu * (_width - 2*RADIUS);
			drawSlider();
		}
		
/**
 *  Current slider calue between 0 and 1
 */
		public function get value():Number {
			return _value;
		}
		
/**
 *  Set width of slider
 */
		public function set fixwidth(valuu:Number):void {
			_width = valuu;
			value = _value;
		}
		
		
		public function destructor():void {
			_knob.removeEventListener(MouseEvent.MOUSE_DOWN, mouseDown);
			stage.removeEventListener(MouseEvent.MOUSE_MOVE, mouseMove);
			stage.removeEventListener(MouseEvent.MOUSE_UP, mouseUp);
		}
	}
}