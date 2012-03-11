package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.SelectionEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.State.Column;
	import Elixys.JSON.State.Sequence;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.text.TextField;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	
	// This sequencer body component is an extension of the ScrollHorizontal class
	public class SequencerBody extends ScrollHorizontal
	{
		/***
		 * Construction
		 **/
		
		public function SequencerBody(screen:Sprite, xml:XML, attributes:Attributes)
		{
			// Call the base constructor
			super(screen, SEQUENCERBODY, attributes);

			// Enable the mask
			scrollRect = new Rectangle(0, 0, attributes.width, attributes.height);

			// Add the window skins
			m_pWindowLeftSkin = AddSkinAt(sequencer_windowLeft, 0);
			m_pWindowRightSkin = AddSkinAt(sequencer_windowRight, 1);
			m_pWindowCenterSkin = AddSkinAt(sequencer_windowCenter, 2);
		}
		
		/***
		 * Member functions
		 **/

		/*
		// Override the hit searching function
		protected override function doSearchHit():void
		{
			// Convert from local to global coordinates
			var pLocalPoint:Point = new Point(_slider.mouseX, _slider.mouseY);
			var pGlobalPoint:Point = _slider.localToGlobal(pLocalPoint);

			// Check for a row click
			for (var nIndex:int = 0; nIndex < m_pHitAreasGlobal.length; ++nIndex)
			{
				if ((m_pHitAreasGlobal[nIndex] as Rectangle).contains(pGlobalPoint.x, pGlobalPoint.y))
				{
					// Dispatch a selection change event, set the selected row index and render
					dispatchEvent(new SelectionEvent(m_pData[nIndex][m_sIDField]));
					m_nSelectedRow = nIndex;
					Render();
					return;
				}
			}
		}
		*/

		// Add a skin
		protected function AddSkinAt(pClass:Class, nIndex:int):MovieClip
		{
			var pMovieClip:MovieClip = new pClass() as MovieClip;
			_slider.addChildAt(pMovieClip, nIndex);
			return pMovieClip;
		}

		// Update the sequencer body
		public function UpdateBody(nComponentID:uint, pSequence:Sequence):void
		{
			// Calculate the required slider width
			var nColumnWidth:Number = attributes.width / Sequencer.VISIBLE_COLUMN_COUNT;
			var nWidth:Number = nColumnWidth * pSequence.Components.length;
			if (nWidth < attributes.width)
			{
				nWidth = attributes.width;
			}
			
			// Force the dimensions of the slider
			var pSlider:Form = _slider as Form;
			pSlider.ForceWidth(nWidth);
			doLayout();

			// Update the window skin positions
			var nWindowHeight:Number = attributes.height * WINDOW_PERCENT_HEIGHT / 100;
			m_pWindowLeftSkin.x = WINDOW_GAP;
			m_pWindowLeftSkin.y = 0;
			m_pWindowLeftSkin.height = nWindowHeight;
			m_pWindowRightSkin.x = nWidth - m_pWindowRightSkin.width - WINDOW_GAP;
			m_pWindowRightSkin.y = 0;
			m_pWindowRightSkin.height = nWindowHeight;
			m_pWindowCenterSkin.x = -67;
			m_pWindowCenterSkin.y = 0;
			m_pWindowCenterSkin.width = nWidth - (WINDOW_GAP * 2) + 175;
			m_pWindowCenterSkin.height = nWindowHeight;
		}

		/***
		 * Member variables
		 **/

		// Sequencer XML
		protected static const SEQUENCERBODY:XML = 
			<frame border="false" />;
		
		// Components
		protected var m_pWindowLeftSkin:MovieClip;
		protected var m_pWindowCenterSkin:MovieClip;
		protected var m_pWindowRightSkin:MovieClip;
		
		// Constants
		protected static var WINDOW_GAP:int = 20;
		protected static var WINDOW_PERCENT_HEIGHT:int = 77;
	}
}
