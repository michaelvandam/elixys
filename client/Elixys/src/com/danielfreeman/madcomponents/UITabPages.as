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
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.geom.Matrix;
	
/**
 *  MadComponents tabbed pages container
 * <pre>
 * &lt;tabPages
 *    id = "IDENTIFIER"
 *    colour = "#rrggbb"
 *    background = "#rrggbb, #rrggbb, ..."
 *    visible = "true|false"
 *    gapV = "NUMBER"
 *    gapH = "NUMBER"
 *    alignH = "left|right|centre"
 *    alignV = "top|bottom|centre"
 *    border = "true|false"
 *    mask = "true|false"
 *    alt = "true|false"
 * /&gt;
 * </pre>
 */
	public class UITabPages extends UIPages {
		
		protected static const PADDING:Number = 1.0;
		
		protected var _buttonBar:Sprite = null;
		protected var _buttons:Array = [];
		protected var _mouseDownTarget:UITabButton = null;
		protected var _colour:uint;
		

		public function UITabPages(screen:Sprite, xml:XML, attributes:Attributes) {
			_colour = attributes.colour;
			initialiseButtonBar(xml,attributes);
			super(screen, xml, attributes);
			_buttonBar.addEventListener(MouseEvent.MOUSE_DOWN, mouseDown);			
			_buttonBar.addEventListener(MouseEvent.MOUSE_UP, mouseUp);
			setChildIndex(_buttonBar, numChildren-1);
		}
		
		
		protected function initialiseButtonBar(xml:XML, attributes:Attributes):void {
			addChild(_buttonBar=new Sprite());
			makeTabButtons(attributes, xml.children().length(), xml.@alt == "true");
			attributes.height -= _buttonBar.height;
			_buttonBar.y = attributes.y + attributes.height+2;
		}
		
		
		protected function mouseDown(event:MouseEvent):void {
			if (event.target is UITabButton) {
				_mouseDownTarget = UITabButton(event.target);
			}
		}
		
		
		protected function mouseUp(event:MouseEvent):void {
			if (_mouseDownTarget && event.target == _mouseDownTarget) {
				goToPage(parseInt(event.target.name));
			}
			_mouseDownTarget = null;
		}

/**
 *  Set the label and icon of a particular tab button
 */
		public function setTab(index:int, label:String, imageClass:Class = null):void {
			var button:UITabButton = UITabButton(_buttons[index]);
			button.text = label;
			if (imageClass)
				button.imageClass = imageClass;
		}
		
		
		protected function superLayout(attributes:Attributes):void {
			super.layout(attributes);
		}
		
/**
 *  Rearrange the layout to new screen dimensions
 */	
		override public function layout(attributes:Attributes):void {
			attributes.height -= _buttonBar.height;
			_buttonBar.y = attributes.y + attributes.height + 2;
			superLayout(attributes);
			var buttonWidth:Number = attributes.width / _buttonBar.numChildren;
			for (var i:int=0; i<_buttonBar.numChildren; i++) {
				var button:UITabButton = UITabButton(_buttonBar.getChildAt(i));
				button.x = i * buttonWidth;
				button.fixwidth = buttonWidth;
			}
			drawTabButtonBackground();
		}
		
/**
 *  Attach new pages to this container
 */	
		override public function attachPages(pages:Array, alt:Boolean = false):void {
			super.attachPages(pages, alt);
			makeTabButtons(_attributes, pages.length, alt);
			_buttonBar.y = attributes.y + attributes.height+2;
		}

/**
 *  Draw the tab buttons
 */	
		protected function makeTabButtons(attributes:Attributes, numberOfPages:int, alt:Boolean):void {
			if (numberOfPages > 0) {
				var buttonWidth:Number = attributes.width / numberOfPages;
				for (var i:int = 0; i < numberOfPages; i++) {
					var _tab:UITabButton = new UITabButton(_buttonBar, i * buttonWidth - 0.5, 0, i.toString(), _colour, alt);
					_buttons.push(_tab);
					_tab.name = i.toString();
					_tab.fixwidth = buttonWidth + 1;
				}
				drawTabButtonBackground();
				UITabButton(_buttons[0]).state = true;
			}
		}
		
/**
 *  Set the colour of the tab buttons
 */	
		public function set colour(value:uint):void {
			_colour = value;
			drawTabButtonBackground();
			for each (var button:UITabButton in _buttons) {
				button.colour = value;
			}
		}
		
/**
 *  Draw the tab buttons background
 */	
		public function drawTabButtonBackground():void {
			var matr:Matrix=new Matrix();
			var gradient:Array = [Colour.lighten(_colour,96),Colour.darken(_colour),Colour.darken(_colour)];
			matr.createGradientBox(width, height, Math.PI/2, 0, 0);
			_buttonBar.graphics.clear();
			_buttonBar.graphics.beginGradientFill(GradientType.LINEAR, gradient, [1.0,1.0,1.0], [0x00,0x80,0xff], matr);
			_buttonBar.graphics.drawRect(0, -PADDING, _buttonBar.width, _buttonBar.height + PADDING);
		}
		
		
		override public function destructor():void {
			_buttonBar.removeEventListener(MouseEvent.MOUSE_DOWN, mouseDown);
			_buttonBar.removeEventListener(MouseEvent.MOUSE_UP, mouseUp);
			super.destructor();
		}
	}
}