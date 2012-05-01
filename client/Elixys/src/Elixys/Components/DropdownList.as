package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.DropdownEvent;
	import Elixys.Extended.Form;
	import Elixys.Extended.ScrollVertical;
	import Elixys.Subviews.SubviewUnitOperationBase;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObjectContainer;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.geom.Rectangle;

	// This dropdown list component is an extension of the scroll vertical class
	public class DropdownList extends ScrollVertical
	{
		/***
		 * Construction
		 **/
		
		public function DropdownList(screen:Sprite, attributes:Attributes)
		{
			// Call the base constructor
			super(screen, DROPDOWNLIST, attributes);
			
			// Our slider is a Form
			m_pSlider = _slider as Form;
		}
		
		/***
		 * Member functions
		 **/

		// Sets the data list and current value
		public function SetList(pValues:Array, sCurrentValue:String, pData:Array = null):void
		{
			// Remember the list
			m_pValues = pValues;
			m_sCurrentValue = sCurrentValue;
			m_pData = pData;
			
			// Update the list
			Update();
			
			// Adjust the positions
			AdjustPositions();
		}

		// Updates the list
		protected function Update():void
		{
			// Adjust the height of the slider
			var nSliderHeight:Number = (SubviewUnitOperationBase.SCROLL_VERTICAL_PADDING * 2) + 
				(SubviewUnitOperationBase.ROWCONTENTHEIGHT * m_pValues.length);
			if (nSliderHeight < attributes.height)
			{
				m_pSlider.ForceHeight(attributes.height);
				scrollEnabled = false;
				doLayout();
			}
			else
			{
				m_pSlider.ForceHeight(nSliderHeight);
				scrollEnabled = true;
				doLayout();
			}

			// Update the number of labels
			var nIndex:int, pLabel:UILabel;
			for (nIndex = 0; nIndex < m_pValues.length; ++nIndex)
			{
				if (m_pLabels.length > nIndex)
				{
					// Get label
					pLabel = m_pLabels[nIndex] as UILabel;
				}
				else
				{
					// Add label
					var pXML:XML =
						<label useEmbedded="true" alignH="left" alignV="bottom">
							<font face="GothamBold" size="18" />
						</label>;
					pLabel = m_pSlider.CreateLabel(pXML, attributes);
					m_pLabels.push(pLabel);
				}
				pLabel.text = m_pValues[nIndex];
			}
			while (m_pLabels.length > m_pValues.length)
			{
				pLabel = m_pLabels.pop();
				m_pSlider.removeChild(pLabel);
			}

			// Update the number of hit areas
			for (nIndex = 0; nIndex < m_pValues.length; ++nIndex)
			{
				if (m_pHitAreas.length <= nIndex)
				{
					// Add hit area
					m_pHitAreas.push(new Rectangle());
				}
			}
			while (m_pHitAreas.length > m_pValues.length)
			{
				m_pHitAreas.pop();
			}
		}
		
		// Adjusts the positions
		protected function AdjustPositions():void
		{
			// Draw the background
			m_pSlider.graphics.clear();
			m_pSlider.graphics.beginFill(Styling.AS3Color(Styling.APPLICATION_BACKGROUND));
			m_pSlider.graphics.drawRect(0, 0, m_pSlider.attributes.width, m_pSlider.attributes.height);
			m_pSlider.graphics.endFill();
			
			// Draw the dividers and set the label positions
			var nOffsetY:Number = SubviewUnitOperationBase.SCROLL_VERTICAL_PADDING;
			m_pSlider.graphics.beginFill(Styling.AS3Color(Styling.UNITOPERATION_DIVIDER));
			var nIndex:int, pLabel:UILabel, pHitArea:Rectangle;
			for (nIndex = 0; nIndex < m_pValues.length; ++nIndex)
			{
				// Draw the top divider
				m_pSlider.graphics.drawRect(0, nOffsetY - (SubviewUnitOperationBase.DIVIDER_HEIGHT / 2), 
					m_pSlider.attributes.width, SubviewUnitOperationBase.DIVIDER_HEIGHT);
				
				// Adjust the label
				pLabel = m_pLabels[nIndex] as UILabel;
				pLabel.x = SubviewUnitOperationBase.HORIZONTALGAP;
				pLabel.y = nOffsetY + ((SubviewUnitOperationBase.ROWCONTENTHEIGHT - pLabel.textHeight) / 2);

				// Set the label color
				if (pLabel.text == m_sCurrentValue)
				{
					pLabel.textColor = Styling.AS3Color(Styling.TEXT_BLUE4);
				}
				else
				{
					pLabel.textColor = Styling.AS3Color(Styling.TEXT_BLACK);
				}
				
				// Set the hit area
				pHitArea = m_pHitAreas[nIndex] as Rectangle;
				pHitArea.x = 0;
				pHitArea.y = nOffsetY;
				pHitArea.width =  m_pSlider.attributes.width;
				pHitArea.height = SubviewUnitOperationBase.ROWCONTENTHEIGHT;

				// Adjust the offset
				nOffsetY += SubviewUnitOperationBase.ROWCONTENTHEIGHT;
			}
			
			// Draw the bottom divider
			m_pSlider.graphics.drawRect(0, nOffsetY - (SubviewUnitOperationBase.DIVIDER_HEIGHT / 2), 
				m_pSlider.attributes.width, SubviewUnitOperationBase.DIVIDER_HEIGHT);
			m_pSlider.graphics.endFill();
		}

		// Overridden search hit function
		protected override function doSearchHit():void
		{
			// Hit test
			var nIndex:int, pHitArea:Rectangle;
			for (nIndex = 0; nIndex < m_pHitAreas.length; ++nIndex)
			{
				pHitArea = m_pHitAreas[nIndex] as Rectangle;
				if (pHitArea.contains(m_pSlider.mouseX, m_pSlider.mouseY))
				{
					// Dispatch a click event
					var pEvent:DropdownEvent = new DropdownEvent(DropdownEvent.ITEMSELECTED);
					pEvent.selectedValue = m_pValues[nIndex];
					if (m_pData)
					{
						pEvent.selectedData = m_pData[nIndex];
					}
					else
					{
						pEvent.selectedData = null;
					}
					dispatchEvent(pEvent);
					return;
				}
			}
		}

		// Overridden function to detect visibility changes
		public override function set visible(bVisible:Boolean):void
		{
			// Add or remove our enter frame event listener
			if (bVisible && !hasEventListener(Event.ENTER_FRAME))
			{
				addEventListener(Event.ENTER_FRAME, OnEnterFrame);
			}
			else if (!bVisible && hasEventListener(Event.ENTER_FRAME))
			{
				removeEventListener(Event.ENTER_FRAME, OnEnterFrame);
			}
			
			// Call the base setter
			super.visible = bVisible;
		}
		
		// Called when we enter a frame
		protected function OnEnterFrame(event:Event):void
		{
			// Check our visibility every 30 frames
			if (++m_nVisibilityCheckCount > 30)
			{
				// Walk the display list to determine our visibility
				var pParent:DisplayObjectContainer = this.parent;
				while (pParent != null)
				{
					if (!pParent.visible)
					{
						// Dispatch a hidden event
						dispatchEvent(new DropdownEvent(DropdownEvent.LISTHIDDEN));
						break;
					}
					pParent = pParent.parent;
				}
				
				// Reset the counter
				m_nVisibilityCheckCount = 0;
			}
		}
		
		/***
		 * Member variables
		 **/
		
		// Dropdown list XML
		protected static const DROPDOWNLIST:XML = 
			<frame mask="true" />;
		
		// List options
		protected var m_pValues:Array;
		protected var m_sCurrentValue:String;
		protected  var m_pData:Array;
		
		// View components
		protected var m_pSlider:Form;
		protected var m_pLabels:Array = new Array();
		protected var m_pHitAreas:Array = new Array();

		// Visibilty check counter
		protected var m_nVisibilityCheckCount:int = 0;
	}
}
