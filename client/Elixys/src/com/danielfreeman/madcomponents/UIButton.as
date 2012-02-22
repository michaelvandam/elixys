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

	import flash.display.Bitmap;
	import flash.display.BitmapData;
	import flash.display.DisplayObject;
	import flash.display.GradientType;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.geom.Matrix;
	import flash.geom.Rectangle;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.getDefinitionByName;
	
/**
  * The button was clicked
 */
	[Event( name="clicked", type="flash.events.Event" )]
	


/**
 *  Button component
 * <pre>
 * &lt;button
 *   id = "IDENTIFIER"
 *   colour = "#rrggbb"
 *   background = "#rrggbb, #rrggbb, ..."
 *   alignH = "left|right|centre|fill"
 *   alignV = "top|bottom|centre|fill"
 *   visible = "true|false"
 *   width = "NUMBER"
 *   height = "NUMBER"
 *   alt = "true|false"
 *   skin = "IMAGE_CLASS_NAME"
 *   clickable = "true|false"
 * /&gt;
 * </pre>
 */
	
	public class UIButton extends MadSprite {
		
		public static const CLICKED:String = "clicked";
	
		protected static const SHADOW_OFFSET:Number = 1.0;
		protected static const FORMAT:TextFormat = new TextFormat("Tahoma", 17, 0xFFFFFF);
		protected static const DARK_FORMAT:TextFormat = new TextFormat("Tahoma", 17, 0x111111);
		protected static const CURVE:Number = 16.0;
		protected static const SIZE_X:Number = 10.0;
		protected static const SIZE_Y:Number = 7.0;
		protected static const TINY_SIZE_Y:Number = 6.0;
		
		protected var _format:TextFormat = FORMAT;
		protected var _darkFormat:TextFormat = DARK_FORMAT;
		protected var _label:UILabel;
		protected var _shadowLabel:UILabel;
		protected var _colour:uint;
		protected var _fixwidth:Number = 0;
		protected var _alpha:Number = 0;
		protected var _colours:Vector.<uint>;
		protected var _gap:Number = SIZE_X;
		protected var _enabled:Boolean = false;
		protected var _sizeY:Number = SIZE_Y;
		protected var _curve:Number;
		protected var _border:Number = 2;
		protected var _skin:Bitmap = null;
		protected var _skinContainer:Sprite = new Sprite();
		protected var _buttonSkin:DisplayObject = null;
		protected var _skinHeight:Number = -1;
		protected var _defaultWidth:Number;
		
	
		public function UIButton(screen:Sprite, xx:Number, yy:Number, text:String, colour:uint = 0x9999AA, colours:Vector.<uint> = null, tiny:Boolean = false) {
			if (tiny) {
				_sizeY = TINY_SIZE_Y;
				_border = 0.5;
			}
			screen.addChild(this);
			x=xx;y=yy;
			_colour = (colours && colours.length==1) ? colours[0] : colour;
			_colours = colours ? colours : new <uint>[];
			init();
			_curve = (_colours.length>3) ? _colours[3] : CURVE;
			if (_colours.length>4)
				_colours = new <uint>[];
			_darkFormat.color = Colour.darken(_colour,-128);
			_format.align = _darkFormat.align = TextFormatAlign.CENTER;
			_shadowLabel = new UILabel(this, _gap-SHADOW_OFFSET, _sizeY-SHADOW_OFFSET -1, " ", _darkFormat);
			_label = new UILabel(this, _gap, _sizeY-1, " ", _format);
			_label.multiline = _shadowLabel.multiline = true;
			this.text = text;
			addEventListener(MouseEvent.MOUSE_DOWN, mouseDown);
			buttonMode = useHandCursor = true;
		}
		
		
		protected function init():void {
			if (_colours.length>3) {
				_gap=Math.max(_colours[3]/3,SIZE_X);
			}
		}
		
		
		protected function mouseDown(event:MouseEvent):void {
			drawButton(true);
			_enabled=true;
			stage.addEventListener(MouseEvent.MOUSE_UP, mouseUp);
		}
		
		
		protected function mouseUp(event:MouseEvent):void {
			drawButton();
			if (_enabled && event.target== this)
				dispatchEvent(new Event(CLICKED));
			stage.removeEventListener(MouseEvent.MOUSE_UP, mouseUp);
			_enabled = false;
		}
		
/**
 * Set button label
 */	
		public function set text(value:String):void {
			if (value=="") {
				value = " ";
			} else if (XML(value).nodeKind() != "text") {
				var xmlString:String = XML(value).toXMLString();
				_label.htmlText = value;
				_shadowLabel.text = "";
			} else {
				_label.text = value;
				_shadowLabel.text = value;
			}
			drawButton();
		}
		
/**
 * Set button width
 */	
		public function set fixwidth(value:Number):void {
			_fixwidth = value;
			drawButton();
		}
		
/**
 * Set button colour
 */	
		public function set colour(value:uint):void {
			_colour = value;
			drawButton();
		}
		
		
		protected function sizeY():Number {
			return 2*_sizeY;
		}
		
		
		protected function drawButton(pressed:Boolean = false):void {
			var width:Number = Math.max(_fixwidth,_label.width + 2 * _gap);
			if (_buttonSkin && (_label.text=="" || _label.text==" ")) {
				_buttonSkin.scaleX = 1.0;
				width = _buttonSkin.width;
			}
			graphics.clear();
			if (_buttonSkin) {
				if (_skin)
					removeChild(_skin);
				_buttonSkin.width = width;

				if (_skinHeight>0)
					_buttonSkin.height = _skinHeight;

				var myBitmapData:BitmapData = new BitmapData(width, _buttonSkin.height, true, 0x00FFFFFF);
				myBitmapData.draw(_skinContainer);
				addChildAt(_skin = new Bitmap(myBitmapData),0);
				_label.y = (_skin.height - _label.height)/2;
				_shadowLabel.y = _label.y-SHADOW_OFFSET;
				if (pressed) {
					graphics.beginFill(UIList.HIGHLIGHT);
					graphics.drawRoundRect(0, 0, _buttonSkin.width, _buttonSkin.height, _curve);
				}
			}
			else {
				var height:Number = _skinHeight>0 ? _skinHeight : _label.height + sizeY();
				var matr:Matrix=new Matrix();
				var gradient:Array = pressed ? [Colour.darken(_colour,128),Colour.lighten(_colour),Colour.darken(_colour)]
										: [Colour.lighten(_colour,80),Colour.darken(_colour),Colour.darken(_colour)];
				matr.createGradientBox(width, height, Math.PI/2, 0, 0);
				if (_colours.length>0) {
					graphics.beginFill(_colours[0]);
				}
				else {
					graphics.beginGradientFill(GradientType.LINEAR, [Colour.darken(_colour),Colour.lighten(_colour)], [1.0,1.0], [0x00,0xff], matr);
				}
				graphics.drawRoundRect(0, 0, width, height, _curve);
				
				if (_colours.length>2 && pressed) {
					graphics.beginFill(_colours[2]);
				}
				else if (_colours.length>1) {
					graphics.beginFill(_colours[1]);
				}
				else {
					graphics.beginGradientFill(GradientType.LINEAR, gradient, [1.0,1.0,1.0], [0x00,0x80,0xff], matr);
				}
				graphics.drawRoundRect(_border, _border, width-2*_border, height-2*_border, _curve);
				if (_skinHeight>0) {
					_label.y = (_skinHeight-_label.height)/2;
					_shadowLabel.y = _label.y - 1;				
				}
			
			}
			if (_fixwidth > _label.width + 2 * _gap) {
				_label.x = (_fixwidth-_label.width)/2;
				_shadowLabel.x = _label.x - 1;
			}
		//	cacheAsBitmap = true;
		}
		
/**
 * Set button skin
 */	
		public function set skin(value:String):void {
			skinClass = getDefinitionByName(value) as Class;
		}
		
		
		public function set skinClass(value:Class):void {
			if (_buttonSkin)
				_skinContainer.removeChild(_buttonSkin);
			_skinContainer.addChild(_buttonSkin = new value());
			drawButton();
		}
		
/**
 * Set height of button skin
 */	
		public function set skinHeight(value:Number):void {
			_skinHeight = value;
			drawButton();
		}
		
		
		public function destructor():void {
			removeEventListener(MouseEvent.MOUSE_DOWN, mouseDown);
			stage.removeEventListener(MouseEvent.MOUSE_UP, mouseUp);
		}
	}
}