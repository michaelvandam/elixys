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
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.TimerEvent;
	import flash.geom.Rectangle;
	import flash.utils.Timer;
	
/**
 * A page has changed
 */
	[Event( name="change", type="flash.events.Event" )]

	
/**
 *  MadComponents pages container
 * <pre>
 * &lt;pages
 *    id = "IDENTIFIER"
 *    colour = "#rrggbb"
 *    background = "#rrggbb, #rrggbb, ..."
 *    visible = "true|false"
 *    gapV = "NUMBER"
 *    gapH = "NUMBER"
 *    width = "NUMBER"
 *    height = "NUMBER"
 *    alignH = "left|right|centre|fill"
 *    alignV = "top|bottom|centre|fill"
 *    border = "true|false"
 *    mask = "true|false"
 * /&gt;
 * </pre>
 */
	public class UIPages extends Sprite implements IContainerUI {
	
		public static const SLIDE_LEFT:String = "left";
		public static const SLIDE_RIGHT:String = "right";
		public static const SLIDE_UP:String = "up";
		public static const SLIDE_DOWN:String = "down";
		public static const DRAWER_UP:String = "drawerUp";
		public static const DRAWER_DOWN:String = "drawerDown";
		
		protected static const DELTA:int = 40;
		protected static const STEPS:int = 8;
		protected static const PADDING:Number = 10.0;
		protected static const DIM_ALPHA:Number = 0.4;
		public static var DRAWER_HEIGHT:Number = 250;

		protected var _pages:Array = [];
		protected var _page:int = 0;
		protected var _thisPage:DisplayObject = null;
		protected var _lastPage:DisplayObject;
		protected var _slideX:Number = 0;
		protected var _slideY:Number = 0;
		protected var _slideTimer:Timer = new Timer(DELTA, STEPS);
		
		protected var _xml:XML;
		protected var _attributes:Attributes;
		protected var _drawer:UIForm;
		protected var _transition:String;
		protected var _lastPageIndex:int;
		protected var _border:Boolean = true;
		
		
		public function UIPages(screen:Sprite, xml:XML, attributes:Attributes) {
			
			_xml = xml;
			_attributes = attributes.copy();
			_attributes.x=0;_attributes.y=0;
		//	_border = xml.@border.length()==0 || xml.@border[0]!="false";
			
			screen.addChildAt(this,0);
			var children:XMLList = xml.children();
			for each (var child0:XML in children) if (child0.nodeKind() != "text") {
				if (child0.localName()!="data") {
					var childstr:String = child0.toXMLString();
					var child:XML = XML('<page lazyRender="'+(xml.@lazyRender)+'">'+childstr+'</page>');
					var newAttributes:Attributes = _attributes.copy();
					newAttributes.parse(child0);
					if (child0.@border!="false") {
						addPadding(child0.localName(), newAttributes);
					}
					var page:* = new UI.FormClass(this, child, newAttributes);
					_attributes.position(page);
					page.visible = false;
					_pages.push(page);
				}
			}
			if (_pages.length>0) {
				_thisPage = _pages[0];
				_page = 0;
				_thisPage.visible = true;
			}
			_slideTimer.addEventListener(TimerEvent.TIMER,slide);
			
			if (xml.@mask.length()>0 && xml.@mask[0]!="false")
				scrollRect = new Rectangle(0,0,attributes.width,attributes.height);
			
			UI.drawBackgroundColour(attributes.backgroundColours, attributes.width, attributes.height, this);
		}
		
/**
 *  An array of pages inside this container
 */
		public function get pages():Array {
			return _pages;
		}
		
		
		public function get attributes():Attributes {
			return _attributes;
		}
		
		
		public function get xml():XML {
			return _xml;
		}
		
/**
 *  Rearrange the layout to new screen dimensions
 */	
		public function layout(attributes:Attributes):void {
			var children:XMLList = _xml.children();
			var idx:int = 0;
			_attributes = attributes.copy();
			_attributes.x=0;_attributes.y=0;
			UI.drawBackgroundColour(_attributes.backgroundColours, _attributes.width, _attributes.height, this);
			for (var i:int = 0; i<children.length(); i++) {
				var childXML:XML = children[i];
				if (childXML.localName()!="data" && childXML.nodeKind() != "text") {
					var child:XML = XML("<page>"+childXML.toXMLString()+"</page>");
					var newAttributes:Attributes = _attributes.copy();
					newAttributes.parse(childXML);
					if (childXML.@border!="false") {
						addPadding(childXML.localName(),newAttributes);
					}
					var page:IContainerUI = _pages[idx];
					page.layout(newAttributes);
					if (page == _drawer) {
						_drawer.y = _attributes.height  + _attributes.x - DRAWER_HEIGHT;
						drawShade();
					}
					else {
						_attributes.position(DisplayObject(page));
					}
					idx++;
				}
			}
			if (scrollRect)
				scrollRect = new Rectangle(0,0,attributes.width,attributes.height);
		}
		
/**
 *  Add border padding around a page
 */	
		protected function addPadding(localName:String,newAttributes:Attributes):void {
			if (localName.toLowerCase().indexOf("pages")<0 && localName.toLowerCase().indexOf("list")<0 && localName.toLowerCase().indexOf("navigation")<0 && localName.toLowerCase().indexOf("scroll")<0 && localName!="viewFlipper" && localName!="frame") {
				newAttributes.x+=PADDING;
				newAttributes.y+=PADDING;
				newAttributes.width-=2*PADDING;
				newAttributes.height-=2*PADDING;
				newAttributes.hasBorder=true;
			}
		}
		
/**
 *  Go to next page
 */	
		public function nextPage(transition:String=""):void {
			if (!_slideTimer.running && !_lastPage && _page < _pages.length-1) {
				_lastPageIndex = _page;
				_lastPage = _pages[_page];
				_page++;
				_thisPage = _pages[_page];
				_thisPage.visible = true;
				doTransition(transition);
			}
		}
		
/**
 *  Go to previous page
 */	
		public function previousPage(transition:String=""):void {
			if (!_slideTimer.running && !_lastPage && _page > 0) {
				_lastPageIndex = _page;
				_lastPage = _pages[_page];
				_page--;
				_thisPage = _pages[_page];
				_thisPage.visible = true;
				doTransition(transition);
			}
		}
		
/**
 *  Attach new pages to this container
 */	
		public function attachPages(pages:Array, alt:Boolean = false):void {
			_pages = pages;
			for (var i:int = 1; i<pages.length; i++)
				DisplayObject(pages[i]).visible = false;
		}
		
/**
 *  Page transition
 */	
		protected function doTransition(transition:String):void {
			_transition = transition;
			_thisPage.x = _attributes.x;
			_thisPage.y = _attributes.y;
			switch (transition) {
				case SLIDE_LEFT:	_thisPage.x = _attributes.width + _attributes.x;
									startSlide();
									break;
				case SLIDE_RIGHT:	_thisPage.x = - _attributes.width + _attributes.x;
									startSlide();
									break;
				case SLIDE_UP:		_thisPage.y = _attributes.height + _attributes.y;
									startSlide();
									break;
				case SLIDE_DOWN:	startSlide((_attributes.height + _attributes.y)/STEPS);
									break;
				case DRAWER_UP:		_drawer = UIForm(_thisPage);
									drawShade();
									_thisPage.y = _attributes.height  + _attributes.y;
									startSlide(-DRAWER_HEIGHT/STEPS);
									break;
				case DRAWER_DOWN:	_thisPage.y = _attributes.height  + _attributes.x - DRAWER_HEIGHT;
									startSlide((_attributes.height + _attributes.y)/STEPS);
									_drawer = null;
									break;
				default:			_lastPage.visible = false;
									_lastPage = null;
									dispatchEvent(new Event(Event.CHANGE));
			}
		}
		
/**
 *  Create a translucent shade for sliding drawer
 */	
		protected function drawShade():void {
			_drawer.graphics.clear();
			_drawer.graphics.beginFill(0x000000,DIM_ALPHA);
			var height:Number = _attributes.height - DRAWER_HEIGHT;
			_drawer.graphics.drawRect(0, -height, _attributes.width, height);
			_drawer.graphics.beginFill(0x000000);
			_drawer.graphics.drawRect(0, -4, _attributes.width, 4);
		}
		
/**
 *  Start slide transition
 */	
		protected function startSlide(slideY:Number = 0):void {
			_thisPage.cacheAsBitmap=true;
			_lastPage.cacheAsBitmap=true;
			_slideX = (_attributes.x - _thisPage.x)/STEPS;
			_slideY = (slideY==0) ? (_attributes.y - _thisPage.y)/STEPS : slideY;
			_slideTimer.reset();
			_slideTimer.start();
			dispatchEvent(new Event(Event.CHANGE));
		}
		
/**
 *  Is this a simple transition, left right, or change
 */	
		protected function isSimpleTransition(transition:String):Boolean {
			return transition=="" || transition==SLIDE_LEFT || transition==SLIDE_RIGHT;
		}
		
/**
 *  Animate slide transition
 */	
		protected function slide(event:TimerEvent):void {
			_lastPage.x+=_slideX;
			_thisPage.x+=_slideX;
			_thisPage.y+=_slideY;
			if (Timer(event.currentTarget).currentCount == STEPS) {
				_slideTimer.stop();
				_thisPage.cacheAsBitmap=false;
				if (_transition == SLIDE_DOWN || _transition == DRAWER_DOWN) {
					_thisPage.visible = false;
				}
				else if (_transition != SLIDE_UP && _transition != DRAWER_UP) {
					removeLastPage();
				}
				
				if (!isSimpleTransition(_transition)) {
					_page = _lastPageIndex;
				}
			}
		}
		
/**
 *  Make the previous page invisible
 */	
		protected function removeLastPage():void {
			_lastPage.visible = false;
			_lastPage = null;
		}
		
/**
 *  Change page
 */	
		public function goToPage(page:int, transition:String = ""):void {
			if (_slideTimer.running) return;
			_lastPageIndex = _page;
			if (page == _page && isSimpleTransition(transition)) return;
			_lastPage = _pages[_page];
			_page = page;
			_thisPage = _pages[_page];
			_thisPage.visible = true;
			doTransition(transition);
		}
		
/**
 *  Page number
 */	
		public function get pageNumber():int {
			return _page;
		}
		
/**
 *  Clear pages
 */	
		public function clear():void {
			for each (var view:IContainerUI in _pages)
				view.clear();
		}
		
/**
 *  Search for component by id
 */
		public function findViewById(id:String, row:int = -1, group:int = -1):DisplayObject {
			for each (var view:DisplayObject in _pages) {
				if (view.name == id) {
					return view;
				}
				else {
					if (view is IContainerUI) {
						var result:DisplayObject = IContainerUI(view).findViewById(id, row, group);
						if (result)
							return result;
					}
				}
			}
			return null;
		}
		
		
		public function destructor():void {
			_slideTimer.removeEventListener(TimerEvent.TIMER,slide);
			for each (var view:IContainerUI in _pages)
				view.destructor();
		}
		
	}
}
