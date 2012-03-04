package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.ButtonEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.State.Tab;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.GraphicsPathCommand;
	import flash.display.Shape;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	
	// This tab bar component is an extension of our extended Form class
	public class TabBar extends Form
	{
		/***
		 * Construction
		 **/
		
		public function TabBar(screen:Sprite, xml:XML, attributes:Attributes)
		{
			// Call the base constructor
			super(screen, TAB, attributes);

			// Save text font details
			if (xml.@fontFace.length() > 0)
			{
				m_sFontFace = xml.@fontFace[0];
			}
			if (xml.@fontSize.length() > 0)
			{
				m_nFontSize = xml.@fontSize[0];
			}
			if (xml.@textColor.length() > 0)
			{
				m_nTextColor = Styling.AS3Color(xml.@textColor[0]);
			}
			if (xml.@selectedTextColor.length() > 0)
			{
				m_nSelectedTextColor = Styling.AS3Color(xml.@selectedTextColor[0]);
			}
			
			// Remember the text padding
			if (xml.@textpaddinghorizontal.length() > 0)
			{
				m_nTextPaddingHorizontal = xml.@textpaddinghorizontal[0];
			}
			if (xml.@textpaddingvertical.length() > 0)
			{
				m_nTextPaddingVertical = xml.@textpaddingvertical[0];
			}
			
			// Add event listeners
			addEventListener(MouseEvent.MOUSE_DOWN, OnMouseDown);
		}
		
		/***
		 * Member functions
		 **/

		// Update the tabs
		public function UpdateTabs(pTabs:Array, sCurrentTabID:String):void
		{
			// Set the tabs
			m_pTabs = pTabs;
			
			// Adjust the number of labels to match the number from the server
			var pLabel:UILabel, pTab:Tab;
			if (m_pLabels.length != m_pTabs.length)
			{
				while (m_pLabels.length < m_pTabs.length)
				{
					var pXML:XML =
						<label useEmbedded="true" alignH="left" alignV="bottom">
							<font face={m_sFontFace} size={m_nFontSize} />
						</label>;
					pLabel = CreateLabel(pXML, attributes);
					var pTextFormat:TextFormat = pLabel.getTextFormat();
					pTextFormat.align = TextFormatAlign.CENTER;
					pLabel.setTextFormat(pTextFormat);
					pLabel.textColor = m_nTextColor;
					m_pLabels.push(pLabel);
				}
				while (m_pLabels.length > m_pTabs.length)
				{
					pLabel = m_pLabels.pop();
					removeChild(pLabel);
				}
			}
			
			// Set the label text and currently selected tab ID
			for (var nIndex:int = 0; nIndex < m_pTabs.length; ++nIndex)
			{
				pLabel = m_pLabels[nIndex] as UILabel;
				pTab = m_pTabs[nIndex] as Tab;
				pLabel.text = pTab.Text;
				pLabel.width = pLabel.textWidth + 5;
				pLabel.height = pLabel.textHeight;
				if (pTab.ID == sCurrentTabID)
				{
					m_nSelectedTab = nIndex;
				}
			}

			// Render the tab bar
			Render(true);
		}

		// Render the tab bar
		protected function Render(bFullUpdate:Boolean = false):void
		{
			// Get the parent width and height
			var nWidth:Number = (parent as Form).attributes.width;
			var nHeight:Number = (parent as Form).attributes.height;
			
			// Only do a full update if the size has changed or our flag is set
			var pHitRectLocal:Rectangle, pHitRectGlobal:Rectangle;
			if (bFullUpdate || (nWidth != m_nLastWidth) || (nHeight != m_nLastHeight))
			{
				// Update the tab label and hit positions
				var nIndex:int, pTab:Tab, pLabel:UILabel;
				var nTextX:Number = TABBAR_OFFSET + m_nTextPaddingHorizontal;
				var pUpperLeftLocal:Point = new Point();
				var pLowerRightLocal:Point = new Point();
				var pUpperLeftGlobal:Point = new Point();
				var pLowerRightGlobal:Point = new Point();
				while (m_pTabHitAreasLocal.length)
				{
					m_pTabHitAreasLocal.pop();
				}
				while (m_pTabHitAreasGlobal.length)
				{
					m_pTabHitAreasGlobal.pop();
				}
				for (nIndex = 0; nIndex < m_pTabs.length; ++nIndex)
				{
					// Get references to our objects
					pTab = m_pTabs[nIndex] as Tab;
					pLabel = m_pLabels[nIndex] as UILabel;
	
					// Set the text position
					pLabel.x = nTextX;
					pLabel.y = nHeight - pLabel.height - m_nTextPaddingVertical;
	
					// Add the local and global hit positions
					pUpperLeftLocal.x = pLabel.x - m_nTextPaddingHorizontal;
					pUpperLeftLocal.y = pLabel.y - m_nTextPaddingVertical;
					pLowerRightLocal.x = pLabel.x + pLabel.width + m_nTextPaddingHorizontal;
					pLowerRightLocal.y = nHeight;
					pHitRectLocal = new Rectangle(pUpperLeftLocal.x, pUpperLeftLocal.y, pLowerRightLocal.x - pUpperLeftLocal.x,
						pLowerRightLocal.y - pUpperLeftLocal.y);
					m_pTabHitAreasLocal.push(pHitRectLocal);
					pUpperLeftGlobal = localToGlobal(pUpperLeftLocal);
					pLowerRightGlobal = localToGlobal(pLowerRightLocal);
					pHitRectGlobal = new Rectangle(pUpperLeftGlobal.x, pUpperLeftGlobal.y, pLowerRightGlobal.x - pUpperLeftGlobal.x,
						pLowerRightGlobal.y - pUpperLeftGlobal.y);
					m_pTabHitAreasGlobal.push(pHitRectGlobal);
					
					// Set the text color
					if (nIndex == m_nSelectedTab)
					{
						pLabel.textColor = m_nSelectedTextColor;
					}
					else
					{
						pLabel.textColor = m_nTextColor;
					}
	
					// Update our horizontal offset
					nTextX += pLabel.width + (2 * m_nTextPaddingHorizontal);
				}
			
				// Update the size
				m_nLastWidth = nWidth;
				m_nLastHeight = nHeight;
			}

			// Draw the pressed tab background
			graphics.clear();
			var nX:Number, nY:Number;
			if (m_nPressedTab != -1)
			{
				pHitRectLocal = m_pTabHitAreasLocal[m_nPressedTab] as Rectangle;
				nX = pHitRectLocal.x + (LINE_WIDTH / 2) + TABPRESSED_GAP;
				nY = pHitRectLocal.y + TABPRESSED_GAP;
				graphics.beginFill(Styling.AS3Color(Styling.TABBAR_PRESSED));
				graphics.drawRoundRect(nX, nY, pHitRectLocal.width - TABPRESSED_GAP - LINE_WIDTH, pHitRectLocal.height - LINE_WIDTH,
					TABPRESSED_CURVE, TABPRESSED_CURVE);
				graphics.endFill();
			}

			// Draw the tab outline
			pHitRectLocal = m_pTabHitAreasLocal[m_nSelectedTab] as Rectangle;
			graphics.lineStyle(LINE_WIDTH, Styling.AS3Color(Styling.TABBAR_LINE));
			graphics.moveTo(TABBAR_OFFSET, nHeight - LINE_WIDTH);
			graphics.lineTo(pHitRectLocal.x, nHeight - LINE_WIDTH);
			graphics.lineTo(pHitRectLocal.x, pHitRectLocal.y + LINE_CURVE);
			graphics.curveTo(pHitRectLocal.x, pHitRectLocal.y, pHitRectLocal.x + LINE_CURVE, pHitRectLocal.y);
			graphics.lineTo(pHitRectLocal.x + pHitRectLocal.width - LINE_CURVE, pHitRectLocal.y);
			graphics.curveTo(pHitRectLocal.x + pHitRectLocal.width, pHitRectLocal.y, pHitRectLocal.x + pHitRectLocal.width,
				pHitRectLocal.y + LINE_CURVE);
			graphics.lineTo(pHitRectLocal.x + pHitRectLocal.width, nHeight - LINE_WIDTH);
			graphics.lineTo(nWidth - TABBAR_OFFSET, nHeight - LINE_WIDTH);
		}

		// Called when the user presses the mouse button
		protected function OnMouseDown(event:MouseEvent):void
		{
			// Check for a tab click
			for (var nIndex:int = 0; nIndex < m_pTabHitAreasGlobal.length; ++nIndex)
			{
				// Ignore hits to the selected tab
				if (nIndex == m_nSelectedTab)
				{
					continue;
				}
				
				// Hit test
				if ((m_pTabHitAreasGlobal[nIndex] as Rectangle).contains(event.stageX, event.stageY))
				{
					// Listen for mouse up
					stage.addEventListener(MouseEvent.MOUSE_UP, OnMouseUp);

					// Set the pressed tab index and render
					m_nPressedTab = nIndex;
					Render();
					break;
				}
			}
		}

		// Called when the user releases the mouse button
		protected function OnMouseUp(event:MouseEvent):void
		{
			// Remove the event listener
			stage.removeEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
			
			// Check if the mouse was released over the pressed tab
			if ((m_pTabHitAreasGlobal[m_nPressedTab] as Rectangle).contains(event.stageX, event.stageY))
			{
				// Dispatch a click event
				dispatchEvent(new ButtonEvent((m_pTabs[m_nPressedTab] as Tab).ID));
			}
			
			// Release the tab and render
			m_nPressedTab = -1;
			Render();
		}
		
		/***
		 * Member variables
		 **/
		
		// Tab bar component XML
		protected static const TAB:XML = 
			<frame alignV="fill" alignH="fill" background={Styling.APPLICATION_BACKGROUND}/>;

		// Constants
		protected var TABBAR_OFFSET:int = 15;
		protected var LINE_CURVE:int = 5;
		protected var LINE_WIDTH:int = 3;
		protected var TABPRESSED_GAP:int = 1;
		protected var TABPRESSED_CURVE:int = 8;

		// Text details
		protected var m_sFontFace:String = "";
		protected var m_nFontSize:uint = 0;
		protected var m_nTextColor:uint = 0;
		protected var m_nSelectedTextColor:uint = 0;

		// Tab and label arrays
		protected var m_pTabs:Array = new Array();
		protected var m_pLabels:Array = new Array();
		
		// Text padding
		protected var m_nTextPaddingHorizontal:int = 0;
		protected var m_nTextPaddingVertical:int = 0;
		
		// Selected and pressed tab indicies
		protected var m_nSelectedTab:int = 0;
		protected var m_nPressedTab:int = -1;
		
		// Tab hit areas
		protected var m_pTabHitAreasLocal:Array = new Array();
		protected var m_pTabHitAreasGlobal:Array = new Array();
		
		// Last know size
		protected var m_nLastWidth:Number = 0;
		protected var m_nLastHeight:Number = 0;
	}
}
