package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.*;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.Components.Components;
	import Elixys.JSON.State.State;
	
	import com.andymoore.CachedSprite;
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Bitmap;
	import flash.display.BitmapData;
	import flash.display.BlendMode;
	import flash.display.DisplayObjectContainer;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.events.TimerEvent;
	import flash.geom.Matrix;
	import flash.geom.Rectangle;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.*;
	
	// This sequence tools component is an extension of our extended Form class
	public class SequenceTools extends Form
	{
		/***
		 * Construction
		 **/
		
		public function SequenceTools(screen:Sprite, xml:XML, attributes:Attributes, nUnitOperationWidth:Number,
									  nButtonSkinWidth:Number, pElixys:Elixys)
		{
			// Call the base constructor
			super(screen, SEQUENCETOOLS, attributes);

			// Extract input parameters
			if (xml.@fontface.length() > 0)
			{
				m_sFontFace = xml.@fontface[0];
			}
			if (xml.@fontsize.length() > 0)
			{
				m_nFontSize = parseInt(xml.@fontsize[0]);
			}
			if (xml.@enabledtextcolor.length() > 0)
			{
				m_nEnabledTextColor = Styling.AS3Color(xml.@enabledtextcolor[0]);
			}
			if (xml.@pressedtextcolor.length() > 0)
			{
				m_nPressedTextColor = Styling.AS3Color(xml.@pressedtextcolor[0]);
			}
			
			// Remember the elixys reference and button width
			m_pElixys = pElixys;
			m_nButtonWidth = nButtonSkinWidth;
			
			// Add event listeners
			addEventListener(MouseEvent.MOUSE_DOWN, OnMouseDown);
			
			// Create the timer
			m_pHoldTimer = new Timer(50, 1);
			m_pHoldTimer.addEventListener(TimerEvent.TIMER_COMPLETE, OnHoldTimer);
		}
		
		/***
		 * Member functions
		 **/
		
		// Sets the sequencer
		public function SetSequencer(pSequencer:Sequencer):void
		{
			m_pSequencer = pSequencer;
		}

		// Updates
		public function Update():void
		{
			// Initialize if this is our first call
			if (!m_bInitialized)
			{
				// Add skins and labels for each unit operation
				m_pSupportedOperations = m_pElixys.GetConfiguration().SupportedOperations;
				var nIndex:int, pClass:Class;
				for (nIndex = 0; nIndex < m_pSupportedOperations.length; ++nIndex)
				{
					// Add a hit area
					m_pHitAreas.push(new Rectangle());
					
					// Add button background skins
					m_pButtonUpSkins.push(Utils.AddSkin(tools_btn_up, true, this, m_nButtonWidth));
					m_pButtonDownSkins.push(Utils.AddSkin(tools_btn_down, false, this, m_nButtonWidth));
					
					// Add unit operation up and down skins
					var nUnitOperationSkinHeight:Number = m_pButtonUpSkins[0].height - 
						(SequencerBody.ICON_PADDING * 2) - SequencerBody.ICON_GAP - SequencerBody.TEXT_HEIGHT;
					pClass = Components.GetUpSkin(m_pSupportedOperations[nIndex]);
					m_pUnitOperationUpSkins.push(Utils.AddSkin(pClass, true, this, 0, nUnitOperationSkinHeight));
					pClass = Components.GetDownSkin(m_pSupportedOperations[nIndex]);
					m_pUnitOperationDownSkins.push(Utils.AddSkin(pClass, false, this, 0, nUnitOperationSkinHeight));

					// Add a unit operation label
					m_pUnitOperationLabels.push(Utils.AddLabel(m_pSupportedOperations[nIndex], this, m_sFontFace,
						m_nFontSize, m_nEnabledTextColor));
				}
				
				// Set the flag
				m_bInitialized = true;
			}
			
			// Adjust our positions if our dimensions have changed
			var pParent:Form = parent as Form;
			if ((pParent.attributes.width != m_nLastWidth) ||
				(pParent.attributes.height != m_nLastHeight))
			{
				AdjustPositions();
				m_nLastWidth = pParent.attributes.width;
				m_nLastHeight = pParent.attributes.height;
			}
		}

		// Adjust the unit operation positions
		protected function AdjustPositions():void
		{
			// Adjust each unit operation
			var nInitialOffsetX:Number = (attributes.width - (m_nButtonWidth * UNITOPERATION_HORIZONTAL_COUNT) -
				(UNITOPERATION_HORIZONTAL_GAP * (UNITOPERATION_HORIZONTAL_COUNT - 1))) / 2;
			var nOffsetX:Number = nInitialOffsetX, nOffsetY:Number = UNITOPERATION_TOP_GAP;
			var pLabel:UILabel;
			for (var nIndex:int = 0; nIndex < m_pSupportedOperations.length; ++nIndex)
			{
				// Update the skin positions
				m_pButtonUpSkins[nIndex].x = m_pButtonDownSkins[nIndex].x = nOffsetX;
				m_pButtonUpSkins[nIndex].y = m_pButtonDownSkins[nIndex].y = nOffsetY;
				m_pUnitOperationUpSkins[nIndex].x = m_pUnitOperationDownSkins[nIndex].x = 
					m_pButtonUpSkins[nIndex].x + ((m_nButtonWidth - m_pUnitOperationUpSkins[nIndex].width) / 2);
				m_pUnitOperationUpSkins[nIndex].y = m_pUnitOperationDownSkins[nIndex].y = 
					m_pButtonUpSkins[nIndex].y + SequencerBody.ICON_PADDING;
				
				// Update unit operation label position
				pLabel = m_pUnitOperationLabels[nIndex] as UILabel;
				pLabel.width = pLabel.textWidth + 5;
				pLabel.x = m_pButtonUpSkins[nIndex].x + ((m_nButtonWidth - pLabel.width) / 2);
				pLabel.y = m_pUnitOperationUpSkins[nIndex].y + m_pUnitOperationUpSkins[nIndex].height + 
					SequencerBody.ICON_GAP;

				// Update the hit area
				(m_pHitAreas[nIndex] as Rectangle).setTo(nOffsetX, nOffsetY, m_nButtonWidth, m_pButtonUpSkins[nIndex].height);
				
				// Adjust the offsets
				if (((nIndex + 1) % UNITOPERATION_HORIZONTAL_COUNT) == 0)
				{
					nOffsetX = nInitialOffsetX;
					nOffsetY += m_pButtonUpSkins[nIndex].height + UNITOPERATION_VERTICAL_GAP;
				}
				else
				{
					nOffsetX += m_nButtonWidth + UNITOPERATION_HORIZONTAL_GAP;
				}
			}
		}
		
		// Called when the user presses the mouse button
		protected function OnMouseDown(event:MouseEvent):void
		{
			// Check for button clicks
			for (var nIndex:int = 0; nIndex < m_pHitAreas.length; ++nIndex)
			{
				if ((m_pHitAreas[nIndex] as Rectangle).contains(mouseX, mouseY))
				{
					// Press the button and wait for mouse up
					m_nPressedIndex = nIndex;
					PressButton(m_nPressedIndex);
					stage.addEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
					m_pHoldTimer.start();
					break;
				}
			}
		}
		
		// Called when the user releases the mouse button
		protected function OnMouseUp(event:MouseEvent):void
		{
			// Remove the event listener and release the button
			m_pHoldTimer.stop();
			stage.removeEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
			ReleaseButton(m_nPressedIndex);
			m_nPressedIndex = -1;
		}
		
		// Draws the button in the pressed state
		protected function PressButton(nIndex:int):void
		{
			(m_pButtonUpSkins[nIndex] as Sprite).visible = false;
			(m_pButtonDownSkins[nIndex] as Sprite).visible = true;
			(m_pUnitOperationUpSkins[nIndex] as Sprite).visible = false;
			(m_pUnitOperationDownSkins[nIndex] as Sprite).visible = true;
			(m_pUnitOperationLabels[nIndex] as UILabel).textColor = m_nPressedTextColor;
		}
		
		// Draws the button in the released state
		protected function ReleaseButton(nIndex:int):void
		{
			(m_pButtonUpSkins[nIndex] as Sprite).visible = true;
			(m_pButtonDownSkins[nIndex] as Sprite).visible = false;
			(m_pUnitOperationUpSkins[nIndex] as Sprite).visible = true;
			(m_pUnitOperationDownSkins[nIndex] as Sprite).visible = false;
			(m_pUnitOperationLabels[nIndex] as UILabel).textColor = m_nEnabledTextColor;
		}
		
		// Called when the user clicks and holds a unit operation
		protected function OnHoldTimer(event:TimerEvent):void
		{
			// Remove the event listener
			stage.removeEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
			
			// Ignore if a unit operation isn't pressed
			if (m_nPressedIndex == -1)
			{
				return;
			}

			// Release the button
			ReleaseButton(m_nPressedIndex);

			// Duplicate the pressed unit operation
			var pDragTarget:Sprite = new Sprite();
			stage.addChild(pDragTarget);
			var pBackgroundSkin:Sprite = Utils.AddSkin(tools_btn_up, true, pDragTarget, m_nButtonWidth);
			var pForegroundSkin:Sprite = Utils.AddSkin(Components.GetUpSkin(m_pSupportedOperations[m_nPressedIndex]),
				true, pDragTarget, 0, (m_pUnitOperationUpSkins[m_nPressedIndex] as Sprite).height);
			pForegroundSkin.height = pBackgroundSkin.height - (SequencerBody.ICON_PADDING * 2) - SequencerBody.ICON_GAP - 
				SequencerBody.TEXT_HEIGHT;
			pForegroundSkin.scaleX = pForegroundSkin.scaleY;
			pForegroundSkin.x = (m_nButtonWidth - pForegroundSkin.width) / 2;
			pForegroundSkin.y = SequencerBody.ICON_PADDING;
			var pLabel:UILabel = Utils.AddLabel(m_pSupportedOperations[m_nPressedIndex], this, m_sFontFace, m_nFontSize, 
				m_nEnabledTextColor, pDragTarget);
			pLabel.width = pLabel.textWidth + 5;
			pLabel.x = (m_nButtonWidth - pLabel.width) / 2;
			pLabel.y = pForegroundSkin.y + pForegroundSkin.height + SequencerBody.ICON_GAP;

			// Start the drag operation
			m_pSequencer.StartDraggingNew(pDragTarget, m_pSupportedOperations[m_nPressedIndex]);

			// Clear the pressed index
			m_nPressedIndex = -1;
		}

		/***
		 * Member variables
		 **/
		
		// Sequence tools XML
		protected static const SEQUENCETOOLS:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} />;

		// Input parameters
		protected var m_pElixys:Elixys;
		protected var m_nButtonWidth:Number;
		protected var m_sFontFace:String = "";
		protected var m_nFontSize:int = 0;
		protected var m_nEnabledTextColor:uint = 0;
		protected var m_nPressedTextColor:uint = 0;

		// Initialized flag, supported operations list and last know dimensions
		protected var m_bInitialized:Boolean = false;
		protected var m_pSupportedOperations:Array;
		protected var m_nLastWidth:Number = 0;
		protected var m_nLastHeight:Number = 0;

		// Sequencer
		protected var m_pSequencer:Sequencer;

		// Components
		protected var m_pButtonUpSkins:Array = new Array();
		protected var m_pButtonDownSkins:Array = new Array();
		protected var m_pUnitOperationUpSkins:Array = new Array();
		protected var m_pUnitOperationDownSkins:Array = new Array();
		protected var m_pUnitOperationLabels:Array = new Array();

		// Hold timer
		protected var m_pHoldTimer:Timer;

		// Unit operation hit areas
		protected var m_pHitAreas:Array = new Array();
		protected var m_nPressedIndex:int = -1;
		
		// Constants
		protected static var UNITOPERATION_HORIZONTAL_COUNT:int = 3;
		protected static var UNITOPERATION_TOP_GAP:int = 20;
		protected static var UNITOPERATION_HORIZONTAL_GAP:int = 10;
		protected static var UNITOPERATION_VERTICAL_GAP:int = 20;
	}
}
