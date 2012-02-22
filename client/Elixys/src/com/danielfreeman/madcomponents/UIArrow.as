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
	import flash.display.Sprite;
	
/**
 * An arrow component.  Typically used for the end of a list row.
 * <pre>
 * &lt;arrow
 *    id = "IDENTIFIER"
 *    colour = "#rrggbb"
 *    background = "#rrggbb,#rrggbb,..."
 *    alignH = "left|right|centre"
 *    alignV = "top|bottom|centre"
 *    visible = "true|false"
 *    clickable = "true|false"
 * /&gt;
 * </pre>
 */	
	public class UIArrow extends MadSprite
	{
		protected static const BIG_RADIUS:Number = 12.0;
		protected static const RADIUS:Number = 10.0;
		protected static const ARROW_X:Number = 4.0;
		protected static const ARROW_Y:Number = 8.0;
		protected static const ARROW_W:Number = 2.0;
		protected static const OFFSET:Number = 3.0;

		public function UIArrow(screen:Sprite, xx:Number, yy:Number, colour:uint, colours:Vector.<uint>) {
			screen.addChild(this);
			x=xx;y=yy;
			
			if (colours.length>1) {
				graphics.beginFill(colours[1]);
				graphics.drawCircle(BIG_RADIUS - OFFSET, BIG_RADIUS, BIG_RADIUS);
			}
			if (colours.length>0) {
				graphics.beginFill(colours[0]);
				graphics.drawCircle(BIG_RADIUS - OFFSET, BIG_RADIUS, RADIUS);
			}
			else {
				graphics.beginFill(0,0);
				graphics.drawRect( RADIUS - ARROW_X, RADIUS - ARROW_Y, 2 * ARROW_X + 2 * OFFSET, 2 * ARROW_Y);
			}
			
			graphics.beginFill(colour);
			graphics.moveTo(BIG_RADIUS - ARROW_X - ARROW_W, BIG_RADIUS - ARROW_Y);
			graphics.lineTo(BIG_RADIUS - ARROW_X + ARROW_W, BIG_RADIUS - ARROW_Y);
			graphics.lineTo(BIG_RADIUS + ARROW_W, BIG_RADIUS);
			graphics.lineTo(BIG_RADIUS - ARROW_X + ARROW_W, BIG_RADIUS + ARROW_Y);
			graphics.lineTo(BIG_RADIUS - ARROW_X - ARROW_W, BIG_RADIUS + ARROW_Y);
			graphics.lineTo(BIG_RADIUS - ARROW_W, BIG_RADIUS);
			graphics.lineTo(BIG_RADIUS - ARROW_X - ARROW_W, BIG_RADIUS - ARROW_Y);
			
			clickable = mouseEnabled = false;
			buttonMode = useHandCursor = true;
		}
	}
}