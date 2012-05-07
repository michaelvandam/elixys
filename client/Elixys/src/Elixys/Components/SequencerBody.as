package Elixys.Components
{
	import Elixys.Assets.*;
	import Elixys.Events.SelectionEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.Components.ComponentCassette;
	import Elixys.JSON.Components.Components;
	import Elixys.JSON.State.Column;
	import Elixys.JSON.State.Sequence;
	import Elixys.JSON.State.SequenceComponent;
	import Elixys.JSON.State.StateSequence;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.DisplayObjectContainer;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.events.TimerEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.text.TextField;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.*;
	
	// This sequencer body component is an extension of the ScrollHorizontal class
	public class SequencerBody extends ScrollHorizontal
	{
		/***
		 * Construction
		 **/
		
		public function SequencerBody(screen:Sprite, xml:XML, attributes:Attributes)
		{
			// Get our mode
			if (xml.@mode.length() > 0)
			{
				m_sMode = xml.@mode[0];
			}

			// Call the base constructor
			super(screen, SEQUENCERBODY, attributes);

			// Enable the mask
			scrollRect = new Rectangle(0, 0, attributes.width, attributes.height);

			// Add the window skins
			m_pWindowLeftSkin = AddSkinAt(sequencerWindow_left, 0);
			m_pWindowRightSkin = AddSkinAt(sequencerWindow_right, 1);
			m_pWindowCenterSkin = AddSkinAt(sequencerWindow_center, 2);

			// Extract the parameters
			if (xml.@unitoperationfontface.length() > 0)
			{
				m_sUnitOperationFontFace = xml.@unitoperationfontface[0];
			}
			if (xml.@unitoperationfontsize.length() > 0)
			{
				m_nUnitOperationFontSize = parseInt(xml.@unitoperationfontsize[0]);
			}
			if (xml.@unitoperationenabledtextcolor.length() > 0)
			{
				m_nUnitOperationEnabledTextColor = Styling.AS3Color(xml.@unitoperationenabledtextcolor[0]);
			}
			if (xml.@unitoperationdisabledtextcolor.length() > 0)
			{
				m_nUnitOperationDisabledTextColor = Styling.AS3Color(xml.@unitoperationdisabledtextcolor[0]);
			}
			if (xml.@unitoperationactivetextcolor.length() > 0)
			{
				m_nUnitOperationActiveTextColor = Styling.AS3Color(xml.@unitoperationactivetextcolor[0]);
			}
			if (xml.@unitoperationpressedtextcolor.length() > 0)
			{
				m_nUnitOperationPressedTextColor = Styling.AS3Color(xml.@unitoperationpressedtextcolor[0]);
			}
			if (xml.@notefontface.length() > 0)
			{
				m_sNoteFontFace = xml.@notefontface[0];
			}
			if (xml.@notefontsize.length() > 0)
			{
				m_nNoteFontSize = parseInt(xml.@notefontsize[0]);
			}
			if (xml.@noteenabledtextcolor.length() > 0)
			{
				m_nNoteEnabledTextColor = Styling.AS3Color(xml.@noteenabledtextcolor[0]);
			}
			if (xml.@notedisabledtextcolor.length() > 0)
			{
				m_nNoteDisabledTextColor = Styling.AS3Color(xml.@notedisabledtextcolor[0]);
			}
			if (xml.@noteactivetextcolor.length() > 0)
			{
				m_nNoteActiveTextColor = Styling.AS3Color(xml.@noteactivetextcolor[0]);
			}
			if (xml.@numberfontface.length() > 0)
			{
				m_sNumberFontFace = xml.@numberfontface[0];
			}
			if (xml.@numberfontsize.length() > 0)
			{
				m_nNumberFontSize = parseInt(xml.@numberfontsize[0]);
			}
			if (xml.@numberenabledtextcolor.length() > 0)
			{
				m_nNumberEnabledTextColor = Styling.AS3Color(xml.@numberenabledtextcolor[0]);
			}
			if (xml.@numberdisabledtextcolor.length() > 0)
			{
				m_nNumberDisabledTextColor = Styling.AS3Color(xml.@numberdisabledtextcolor[0]);
			}
			if (xml.@numberactivetextcolor.length() > 0)
			{
				m_nNumberActiveTextColor = Styling.AS3Color(xml.@numberactivetextcolor[0]);
			}
			if (xml.@numberactivebackground.length() > 0)
			{
				m_nNumberActiveBackgroundColor = Styling.AS3Color(xml.@numberactivebackgroundcolor[0]);
			}
			
			// Create the timer
			if (m_sMode == Constants.EDIT)
			{
				m_pHoldTimer = new Timer(500, 1);
				m_pHoldTimer.addEventListener(TimerEvent.TIMER_COMPLETE, OnHoldTimer);
			}
			
			// Locates the screen
			var pParent:DisplayObjectContainer = this;
			while (pParent != null)
			{
				if (pParent is Screen)
				{
					m_pScreen = pParent as Screen;
					break;
				}
				pParent = pParent.parent;
			}
		}
		
		/***
		 * Member functions
		 **/

		// Sets the unit operation and button width
		public function SetWidths(nUnitOperationWidth:Number, nButtonWidth:Number):void
		{
			m_nUnitOperationWidth = nUnitOperationWidth;
			m_nButtonSkinWidth = nButtonWidth;
		}
		
		// Sets the sequencer
		public function SetSequencer(pSequencer:Sequencer):void
		{
			m_pSequencer = pSequencer;
		}
		
		// Override the hit searching function
		protected override function doSearchHit():void
		{
			// Only process hits if we are clickable
			if (!_clickable)
			{
				return;
			}
			
			// Ignore clicks if we're in run mode
			if (m_sMode == Constants.RUN)
			{
				return;
			}
			
			// Check for a unit operation click
			var nIndex:int, nUnitOperationIndex:int = 0, pComponent:SequenceComponent;
			for (nIndex = 0; nIndex < m_pSequence.Components.length; ++nIndex)
			{
				// Skip cassettes
				pComponent = m_pSequence.Components[nIndex] as SequenceComponent;
				if (pComponent.ComponentType == ComponentCassette.COMPONENTTYPE)
				{
					continue;
				}

				// Hit test
				if ((m_pHitAreas[nUnitOperationIndex] as Rectangle).contains(_slider.mouseX, _slider.mouseY))
				{
					if (m_nClickState == STATE_CLICKING)
					{
						// Draw the button as pressed
						m_nPressedIndex = nUnitOperationIndex;
						PressButton(m_nPressedIndex);
						
						// Start the hold timer in edit mode
						if (m_sMode == Constants.EDIT)
						{
							m_pHoldTimer.start();
						}
						return;
					}
					else
					{
						// Stop the hold timer in edit mode
						if (m_sMode == Constants.EDIT)
						{
							m_pHoldTimer.stop();
						}
						
						// Ignore if the mouse was released over different button than it was pressed over
						if ((m_nPressedIndex != -1) && (m_nPressedIndex != nUnitOperationIndex))
						{
							ReleaseButton(m_nPressedIndex);
							m_nPressedIndex = -1;
							return;
						}
						
						// Dispatch a selection change event
						dispatchEvent(new SelectionEvent(pComponent.ID));
						return;
					}
				}
				++nUnitOperationIndex;
			}
			
			// Release the button if the mouse was released elsewhere
			if ((m_nClickState == STATE_NONE) && (m_nPressedIndex != -1))
			{
				ReleaseButton(m_nPressedIndex);
				m_nPressedIndex = -1;
			}
		}

		// Overridden to clear any pressed button
		protected override function Reset():void
		{
			// Call the base handler and clear any pressed button
			super.Reset();
			if (m_nPressedIndex != -1)
			{
				ReleaseButton(m_nPressedIndex);
				m_nPressedIndex = -1;
			}
		}

		// Add a skin
		protected function AddSkinAt(pClass:Class, nIndex:int):MovieClip
		{
			var pMovieClip:MovieClip = new pClass() as MovieClip;
			_slider.addChildAt(pMovieClip, nIndex);
			return pMovieClip;
		}

		// Update the sequence
		public function UpdateSequence(pSequence:Sequence):void
		{
			// Ignore if we're dragging
			if (m_nDraggingID != -1)
			{
				return;
			}
			
			// Count the number of non-cassette unit operations
			var nIndex:int, pComponent:SequenceComponent, nUnitOperations:int = 0;
			for (nIndex = 0; nIndex < pSequence.Components.length; ++nIndex)
			{
				pComponent = pSequence.Components[nIndex] as SequenceComponent;
				if (pComponent.ComponentType != ComponentCassette.COMPONENTTYPE)
				{
					++nUnitOperations;
				}
			}
			
			// Calculate the required slider width
			var nWidth:Number = (m_nUnitOperationWidth * nUnitOperations) + (m_pWindowLeftSkin.width + 
				m_pWindowRightSkin.width + (WINDOW_GAP * 2));
			if (nWidth < attributes.width)
			{
				nWidth = attributes.width;
			}
			
			// Force the dimensions of the slider
			var pSlider:Form = _slider as Form;
			pSlider.ForceWidth(nWidth);
			doLayout();

			// Update the window skin positions
			m_nSequencerWindowHeight = attributes.height * WINDOW_PERCENT_HEIGHT / 100;
			m_pWindowLeftSkin.x = WINDOW_GAP;
			m_pWindowLeftSkin.y = 0;
			m_pWindowLeftSkin.height = m_nSequencerWindowHeight;
			m_pWindowRightSkin.x = nWidth - m_pWindowRightSkin.width - WINDOW_GAP;
			m_pWindowRightSkin.y = 0;
			m_pWindowRightSkin.height = m_nSequencerWindowHeight;
			m_pWindowCenterSkin.x = WINDOW_GAP + m_pWindowLeftSkin.width;
			m_pWindowCenterSkin.y = 0;
			m_pWindowCenterSkin.width = nWidth - (m_pWindowLeftSkin.width + m_pWindowRightSkin.width + (WINDOW_GAP * 2));
			m_pWindowCenterSkin.height = m_nSequencerWindowHeight;

			// Clear any selected or pressed unit operations
			m_nSelectedIndex = -1;
			m_nPressedIndex = -1;

			// Create the hit array
			var nOffset:Number = WINDOW_GAP + 10, nUnitOperationIndex:int = 0;
			m_pHitAreas = new Array();
			for (nIndex = 0; nIndex < pSequence.Components.length; ++nIndex)
			{
				// Skip cassettes
				pComponent = pSequence.Components[nIndex] as SequenceComponent;
				if (pComponent.ComponentType == ComponentCassette.COMPONENTTYPE)
				{
					continue;
				}
				
				// Create the hit area
				m_pHitAreas.push(new Rectangle(nOffset, 0, m_nUnitOperationWidth, m_nSequencerWindowHeight));
				nOffset += m_nUnitOperationWidth;
				++nUnitOperationIndex;
			}

			// Adjust the number of button background skins
			while (m_pButtonUpSkins.length < nUnitOperations)
			{
				m_pButtonUpSkins.push(AddSkin(tools_btn_up));
			}
			while (m_pButtonUpSkins.length > nUnitOperations)
			{
				_slider.removeChild(m_pButtonUpSkins.pop());
			}
			while (m_pButtonDownSkins.length < nUnitOperations)
			{
				m_pButtonDownSkins.push(AddSkin(tools_btn_down));
			}
			while (m_pButtonDownSkins.length > nUnitOperations)
			{
				_slider.removeChild(m_pButtonDownSkins.pop());
			}
			while (m_pButtonDisabledSkins.length < nUnitOperations)
			{
				m_pButtonDisabledSkins.push(AddSkin(tools_btn_disabled));
			}
			while (m_pButtonDisabledSkins.length > nUnitOperations)
			{
				_slider.removeChild(m_pButtonDisabledSkins.pop());
			}
			while (m_pButtonActiveSkins.length < nUnitOperations)
			{
				m_pButtonActiveSkins.push(AddSkin(tools_btn_active));
			}
			while (m_pButtonActiveSkins.length > nUnitOperations)
			{
				_slider.removeChild(m_pButtonActiveSkins.pop());
			}

			// Adjust the number and type of unit operation skins
			var pClass:Class;
			nUnitOperationIndex = 0;
			for (nIndex = 0; nIndex < pSequence.Components.length; ++nIndex)
			{
				// Skip cassettes
				pComponent = pSequence.Components[nIndex] as SequenceComponent;
				if (pComponent.ComponentType == ComponentCassette.COMPONENTTYPE)
				{
					continue;
				}

				// Add or update the skins
				pClass = Components.GetUpSkin(pComponent.ComponentType);
				if (nUnitOperationIndex < m_pUnitOperationUpSkins.length)
				{
					if (getQualifiedClassName(m_pUnitOperationUpSkins[nUnitOperationIndex]) != getQualifiedClassName(pClass))
					{
						_slider.removeChild(m_pUnitOperationUpSkins[nUnitOperationIndex]);
						m_pUnitOperationUpSkins[nUnitOperationIndex] = AddSkin(pClass);
					}
				}
				else
				{
					m_pUnitOperationUpSkins.push(AddSkin(pClass));
				}
				pClass = Components.GetDownSkin(pComponent.ComponentType);
				if (nUnitOperationIndex < m_pUnitOperationDownSkins.length)
				{
					if (getQualifiedClassName(m_pUnitOperationDownSkins[nUnitOperationIndex]) != getQualifiedClassName(pClass))
					{
						_slider.removeChild(m_pUnitOperationDownSkins[nUnitOperationIndex]);
						m_pUnitOperationDownSkins[nUnitOperationIndex] = AddSkin(pClass);
					}
				}
				else
				{
					m_pUnitOperationDownSkins.push(AddSkin(pClass));
				}
				pClass = Components.GetDisabledSkin(pComponent.ComponentType);
				if (nUnitOperationIndex < m_pUnitOperationDisabledSkins.length)
				{
					if (getQualifiedClassName(m_pUnitOperationDisabledSkins[nUnitOperationIndex]) != getQualifiedClassName(pClass))
					{
						_slider.removeChild(m_pUnitOperationDisabledSkins[nUnitOperationIndex]);
						m_pUnitOperationDisabledSkins[nUnitOperationIndex] = AddSkin(pClass);
					}
				}
				else
				{
					m_pUnitOperationDisabledSkins.push(AddSkin(pClass));
				}
				pClass = Components.GetActiveSkin(pComponent.ComponentType);
				if (nUnitOperationIndex < m_pUnitOperationActiveSkins.length)
				{
					if (getQualifiedClassName(m_pUnitOperationActiveSkins[nUnitOperationIndex]) != getQualifiedClassName(pClass))
					{
						_slider.removeChild(m_pUnitOperationActiveSkins[nUnitOperationIndex]);
						m_pUnitOperationActiveSkins[nUnitOperationIndex] = AddSkin(pClass);
					}
				}
				else
				{
					m_pUnitOperationActiveSkins.push(AddSkin(pClass));
				}
				
				// Add or update the warning icons
				if (nUnitOperationIndex < m_pUnitOperationWarningIcons.length)
				{
					if (pComponent.ValidationError)
					{
						if (m_pUnitOperationWarningIcons[nUnitOperationIndex] == null)
						{
							m_pUnitOperationWarningIcons[nUnitOperationIndex] = AddSkin(sequencer_invalidMarker);
						}
					}
					else
					{
						if (m_pUnitOperationWarningIcons[nUnitOperationIndex] != null)
						{
							_slider.removeChild(m_pUnitOperationWarningIcons[nUnitOperationIndex]);
							m_pUnitOperationWarningIcons[nUnitOperationIndex] = null;
						}
					}
				}
				else
				{
					if (pComponent.ValidationError)
					{
						m_pUnitOperationWarningIcons.push(AddSkin(sequencer_invalidMarker));
					}
					else
					{
						m_pUnitOperationWarningIcons.push(null);
					}
				}
				++nUnitOperationIndex;
			}
			while (m_pUnitOperationUpSkins.length > nUnitOperations)
			{
				_slider.removeChild(m_pUnitOperationUpSkins.pop());
			}
			while (m_pUnitOperationDownSkins.length > nUnitOperations)
			{
				_slider.removeChild(m_pUnitOperationDownSkins.pop());
			}
			while (m_pUnitOperationDisabledSkins.length > nUnitOperations)
			{
				_slider.removeChild(m_pUnitOperationDisabledSkins.pop());
			}
			while (m_pUnitOperationActiveSkins.length > nUnitOperations)
			{
				_slider.removeChild(m_pUnitOperationActiveSkins.pop());
			}
			while (m_pUnitOperationWarningIcons.length > nUnitOperations)
			{
				var pWarningIcon:MovieClip = m_pUnitOperationWarningIcons.pop();
				if (pWarningIcon != null)
				{
					_slider.removeChild(pWarningIcon);
				}
			}
			
			// Adjust the number of unit operation enabled flags
			while (m_bUnitOperationEnabled.length < nUnitOperations)
			{
				m_bUnitOperationEnabled.push(true);
			}
			while (m_bUnitOperationEnabled.length > nUnitOperations)
			{
				m_bUnitOperationEnabled.pop();
			}
			
			// Adjust the number of unit operation labels
			while (m_pUnitOperationLabels.length < nUnitOperations)
			{
				m_pUnitOperationLabels.push(AddLabel(m_sUnitOperationFontFace, m_nUnitOperationFontSize,
					m_nUnitOperationEnabledTextColor));
			}
			while (m_pUnitOperationLabels.length > nUnitOperations)
			{
				_slider.removeChild(m_pUnitOperationLabels.pop());
			}

			// Adjust the number of unit operation notes
			nUnitOperationIndex = 0;
			for (nIndex = 0; nIndex < pSequence.Components.length; ++nIndex)
			{
				// Skip cassettes
				pComponent = pSequence.Components[nIndex] as SequenceComponent;
				if (pComponent.ComponentType == ComponentCassette.COMPONENTTYPE)
				{
					continue;
				}

				// Update an existing note label or create a new
				if (nUnitOperationIndex < m_pNoteLabels.length)
				{
					if (pComponent.Note != "")
					{
						if (m_pNoteLabels[nUnitOperationIndex] == null)
						{
							m_pNoteLabels[nUnitOperationIndex] = AddLabel(m_sNoteFontFace, m_nNoteFontSize, m_nNoteEnabledTextColor);
						}
					}
					else
					{
						if (m_pNoteLabels[nUnitOperationIndex] != null)
						{
							_slider.removeChild(m_pNoteLabels[nUnitOperationIndex]);
							m_pNoteLabels[nUnitOperationIndex] = null;
						}
					}
				}
				else
				{
					if (pComponent.Note != "")
					{
						m_pNoteLabels.push(AddLabel(m_sNoteFontFace, m_nNoteFontSize, m_nNoteEnabledTextColor));
					}
					else
					{
						m_pNoteLabels.push(null);
					}
				}
				
				// Increment unit operation counter
				++nUnitOperationIndex;
			}
			while (m_pNoteLabels.length > nUnitOperations)
			{
				var pLabel:UILabel = m_pNoteLabels.pop() as UILabel;
				if (pLabel != null)
				{
					_slider.removeChild(pLabel);
				}
			}

			// Adjust the number of number labels
			while (m_pNumberLabels.length < nUnitOperations)
			{
				m_pNumberLabels.push(AddLabel(m_sNumberFontFace, m_nNumberFontSize, m_nNumberEnabledTextColor));
			}
			while (m_pNumberLabels.length > nUnitOperations)
			{
				_slider.removeChild(m_pNumberLabels.pop());
			}
			
			// Remember the sequence and set the selected component
			m_pSequence = pSequence;
			UpdateSelectedComponent(m_nSelectedComponentID);
			
			// Adjust the positions and render
			AdjustPositions();
			Render();
		}

		// Update the selected component
		public function UpdateSelectedComponent(nComponentID:int):void
		{
			// Remember the component ID but do not update if we don't have a sequence
			m_nSelectedComponentID = nComponentID;
			if (m_pSequence == null)
			{
				return;
			}

			// Determine the index of the newly selected unit operation
			var nIndex:int, nUnitOperationIndex:int = 0, pComponent:SequenceComponent;
			var nOldSelectedIndex:int = m_nSelectedIndex;
			m_nSelectedIndex = -1;
			for (nIndex = 0; nIndex < m_pSequence.Components.length; ++nIndex)
			{
				// Skip cassettes
				pComponent = m_pSequence.Components[nIndex] as SequenceComponent;
				if (pComponent.ComponentType == ComponentCassette.COMPONENTTYPE)
				{
					continue;
				}
				
				// Check if this is the current unit operation
				if (pComponent.ID == nComponentID)
				{
					m_nSelectedIndex = nUnitOperationIndex;
				}
				
				// Enable or disable this unit operation if we're in run mode
				if (m_sMode == Constants.RUN)
				{
					m_bUnitOperationEnabled[nUnitOperationIndex] = (m_nSelectedIndex != -1);
				}
				++nUnitOperationIndex;
			}

			// Update the selected unit operation if it changed
			if (m_nSelectedIndex != nOldSelectedIndex)
			{
				// Render the sequencer body
				Render();

				// Adjust the unit operation visibility depending on our mode
				if (m_nSelectedIndex != -1)
				{
					if ((m_sMode == Constants.VIEW) || (m_sMode == Constants.EDIT))
					{
						// Make sure that the previous and next unit operations are visible for view and edit modes.  First
						// check if the previous or current unit operations are off the screen to the left
						var pCurrentUnitOperation:Rectangle = m_pHitAreas[m_nSelectedIndex] as Rectangle;
						if (m_nSelectedIndex > 0)
						{
							var pPreviousUnitOperation:Rectangle = m_pHitAreas[m_nSelectedIndex - 1] as Rectangle;
							if ((-_slider.x) > (pPreviousUnitOperation.x - WINDOW_GAP))
							{
								// Previous unit operation is off the screen to the left
								_slider.x = (-pCurrentUnitOperation.x + m_nUnitOperationWidth);
								if (_slider.x > 0)
								{
									_slider.x = 0;
								}
							}
						}
						else if (m_nSelectedIndex == 0)
						{
							if ((-_slider.x) > (pCurrentUnitOperation.x - WINDOW_GAP))
							{
								// Current unit op off the screen to the left
								_slider.x = (-pCurrentUnitOperation.x + m_nUnitOperationWidth);
								if (_slider.x > 0)
								{
									_slider.x = 0;
								}
							}
						}
	
						// Check if the next or current unit operations are off the screen to the right
						if ((m_nSelectedIndex + 1) < m_pHitAreas.length)
						{
							var pNextUnitOperation:Rectangle = m_pHitAreas[m_nSelectedIndex + 1] as Rectangle;
							if ((-_slider.x) < (pNextUnitOperation.x + m_nUnitOperationWidth - WINDOW_GAP - attributes.width))
							{
								// Next unit operation is off the screen to the right
								_slider.x = (-pNextUnitOperation.x + (m_nUnitOperationWidth * 2));
								if ((-_slider.x + attributes.width) > _slider.width)
								{
									_slider.x = -_slider.width + attributes.width;
								}
							}
						}
						else
						{
							if ((-_slider.x) < (pCurrentUnitOperation.x + m_nUnitOperationWidth - WINDOW_GAP - attributes.width))
							{
								// Current unit op off the screen to the right
								_slider.x = (-pCurrentUnitOperation.x + (m_nUnitOperationWidth * 2));
								if ((-_slider.x + attributes.width) > _slider.width)
								{
									_slider.x = -_slider.width + attributes.width;
								}
							}
						}
					}
					else if (m_sMode == Constants.RUN)
					{
						// Adjust the slider position so the two previous unit operations are visible
						if (m_nSelectedIndex != -1)
						{
							if (m_nSelectedIndex > 1)
							{
								var pUnitOperation:Rectangle = m_pHitAreas[m_nSelectedIndex - 2] as Rectangle;
								_slider.x = -pUnitOperation.x;
								if (_slider.x > 0)
								{
									_slider.x = 0;
								}
							}
							else
							{
								_slider.x = 0;
							}
						}
	
						// Make sure the slide is still within the maximum range
						if ((-_slider.x + attributes.width) > _slider.width)
						{
							_slider.x = -_slider.width + attributes.width;
						}
					}
				}
			}
		}

		// Updates the view component positions
		protected function AdjustPositions():void
		{
			// Ignore if we're dragging
			if (m_nDraggingID != -1)
			{
				return;
			}
			
			// Adjust the visual elements for each unit operation
			var pLabel:UILabel, pComponent:SequenceComponent, nButtonSkinX:Number, nButtonSkinY:Number,
				nUnitOpSkinX:Number, nUnitOpSkinY:Number, pUpSkin:MovieClip, pDownSkin:MovieClip,
				pDisabledSkin:MovieClip, pActiveSkin:MovieClip, pWarningIcon:MovieClip;
			var nButtonUpperGap:Number = m_nSequencerWindowHeight * BUTTON_PERCENT_UPPER_GAP / 100;
			var nButtonLowerGap:Number = m_nSequencerWindowHeight * BUTTON_PERCENT_LOWER_GAP / 100;
			var nOffset:Number = WINDOW_GAP + 10, nUnitOperationIndex:int = 0, nButtonSkinHeight:Number = 0;
			for (var nIndex:int = 0; nIndex < m_pSequence.Components.length; ++nIndex)
			{
				// Skip cassettes
				pComponent = m_pSequence.Components[nIndex] as SequenceComponent;
				if (pComponent.ComponentType == ComponentCassette.COMPONENTTYPE)
				{
					continue;
				}
				
				// Set the positions of the button skins
				pUpSkin = m_pButtonUpSkins[nUnitOperationIndex] as MovieClip;
				pDownSkin = m_pButtonDownSkins[nUnitOperationIndex] as MovieClip;
				pDisabledSkin = m_pButtonDisabledSkins[nUnitOperationIndex] as MovieClip;
				pActiveSkin = m_pButtonActiveSkins[nUnitOperationIndex] as MovieClip;
				nButtonSkinX = nOffset + (Sequencer.BUTTON_GAP / 2);
				pUpSkin.x = pDownSkin.x = pDisabledSkin.x = pActiveSkin.x = nButtonSkinX;
				pUpSkin.y = pDownSkin.y = pDisabledSkin.y = pActiveSkin.y = nButtonUpperGap;
				pUpSkin.width = pDownSkin.width = pDisabledSkin.width = pActiveSkin.width = m_nButtonSkinWidth;
				pUpSkin.scaleY = pDownSkin.scaleY = pDisabledSkin.scaleY = pActiveSkin.scaleY = pUpSkin.scaleX;
				nButtonSkinHeight = pUpSkin.height;

				// Set the positions of the warning icons
				if (m_pUnitOperationWarningIcons[nUnitOperationIndex] != null)
				{
					pWarningIcon = m_pUnitOperationWarningIcons[nUnitOperationIndex] as MovieClip;
					pWarningIcon.height = WARNING_ICON_HEIGHT;
					pWarningIcon.scaleX = pWarningIcon.scaleY;
					pWarningIcon.x = pUpSkin.x + pUpSkin.width - pWarningIcon.width + WARNING_ICON_OFFSETX;
					pWarningIcon.y = pUpSkin.y + WARNING_ICON_OFFSETY;
				}

				// Set the positions of the unit operation skins
				pUpSkin = m_pUnitOperationUpSkins[nUnitOperationIndex] as MovieClip;
				pDownSkin = m_pUnitOperationDownSkins[nUnitOperationIndex] as MovieClip;
				pDisabledSkin = m_pUnitOperationDisabledSkins[nUnitOperationIndex] as MovieClip;
				pActiveSkin = m_pUnitOperationActiveSkins[nUnitOperationIndex] as MovieClip;
				pUpSkin.height = pDownSkin.height = pDisabledSkin.height = pActiveSkin.height = 
					nButtonSkinHeight - (ICON_PADDING * 2) - ICON_GAP - TEXT_HEIGHT;
				pUpSkin.scaleX = pDownSkin.scaleX = pDisabledSkin.scaleX = pActiveSkin.scaleX = pUpSkin.scaleY;
				nUnitOpSkinX = nButtonSkinX + ((m_nButtonSkinWidth - pUpSkin.width) / 2);
				pUpSkin.x = pDownSkin.x = pDisabledSkin.x = pActiveSkin.x = nUnitOpSkinX;
				pUpSkin.y = pDownSkin.y = pDisabledSkin.y = pActiveSkin.y = nButtonUpperGap + ICON_PADDING;
				
				// Adjust unit operation label
				pLabel = m_pUnitOperationLabels[nUnitOperationIndex] as UILabel;
				pLabel.text = pComponent.ComponentType;
				pLabel.width = pLabel.textWidth + 5;
				pLabel.x = nOffset + ((m_nUnitOperationWidth - pLabel.width) / 2);
				pLabel.y = pUpSkin.y + pUpSkin.height + ICON_GAP;
				
				// Adjust the note label
				if (pComponent.Note != "")
				{
					pLabel = m_pNoteLabels[nUnitOperationIndex] as UILabel;
					pLabel.text = unescape(pComponent.Note);
					pLabel.width = pLabel.textWidth + 5;
					pLabel.x = nOffset + ((m_nUnitOperationWidth - pLabel.width) / 2);
					pLabel.y = nButtonUpperGap + nButtonSkinHeight + NOTE_GAP;
				}
				
				// Adjust number label
				pLabel = m_pNumberLabels[nUnitOperationIndex] as UILabel;
				pLabel.text = (nUnitOperationIndex + 1).toString();
				pLabel.width = pLabel.textWidth + 5;
				pLabel.x = nOffset + ((m_nUnitOperationWidth - pLabel.width) / 2);
				pLabel.y = m_nSequencerWindowHeight + ((attributes.height - m_nSequencerWindowHeight - pLabel.height - SELECTED_GAP) / 2);
				
				// Increment offset and index
				nOffset += m_nUnitOperationWidth;
				++nUnitOperationIndex;
			}
		}
		
		// Updates the rendering
		protected function Render():void
		{
			// Ignore if we're dragging
			if (m_nDraggingID != -1)
			{
				return;
			}

			// Update the visibility of the button skins
			var nIndex:int, nUnitOperationIndex:int = 0, pComponent:SequenceComponent;
			for (nIndex = 0; nIndex < m_pSequence.Components.length; ++nIndex)
			{
				// Skip cassettes
				pComponent = m_pSequence.Components[nIndex] as SequenceComponent;
				if (pComponent.ComponentType == ComponentCassette.COMPONENTTYPE)
				{
					continue;
				}

				// Set the visibility of the button skins
				if (nUnitOperationIndex == m_nPressedIndex)
				{
					PressButton(nUnitOperationIndex);
				}
				else if (nUnitOperationIndex == m_nSelectedIndex)
				{
					SelectButton(nUnitOperationIndex);
				}
				else
				{
					ReleaseButton(nUnitOperationIndex);
				}
				++nUnitOperationIndex;
			}
			
			// Draw the background of the currently selected unit operation
			_slider.graphics.clear();
			if (m_nSelectedIndex != -1)
			{
				_slider.graphics.beginFill(Styling.AS3Color(Styling.SCROLLER_SELECTED));
				_slider.graphics.drawRoundRect(WINDOW_GAP + 10 + (m_nSelectedIndex * m_nUnitOperationWidth),
					m_nSequencerWindowHeight, m_nUnitOperationWidth, attributes.height - m_nSequencerWindowHeight - SELECTED_GAP,
					SELECTED_NUMBER_CURVE);
				_slider.graphics.endFill();
			}
		}
		
		// Renders the specified button as pressed
		protected function PressButton(nUnitOperationIndex:int):void
		{
			// Show the down skin
			(m_pButtonUpSkins[nUnitOperationIndex] as MovieClip).visible = false;
			(m_pUnitOperationUpSkins[nUnitOperationIndex] as MovieClip).visible = false;
			(m_pButtonDownSkins[nUnitOperationIndex] as MovieClip).visible = true;
			(m_pUnitOperationDownSkins[nUnitOperationIndex] as MovieClip).visible = true;
			(m_pButtonDisabledSkins[nUnitOperationIndex] as MovieClip).visible = false;
			(m_pUnitOperationDisabledSkins[nUnitOperationIndex] as MovieClip).visible = false;
			(m_pButtonActiveSkins[nUnitOperationIndex] as MovieClip).visible = false;
			(m_pUnitOperationActiveSkins[nUnitOperationIndex] as MovieClip).visible = false;

			// Set the unit operation label colors
			(m_pUnitOperationLabels[nUnitOperationIndex] as UILabel).textColor = m_nUnitOperationPressedTextColor;
		}

		// Renders the specified button as selected
		protected function SelectButton(nUnitOperationIndex:int):void
		{
			// Show the active skin
			(m_pButtonUpSkins[nUnitOperationIndex] as MovieClip).visible = false;
			(m_pUnitOperationUpSkins[nUnitOperationIndex] as MovieClip).visible = false;
			(m_pButtonDownSkins[nUnitOperationIndex] as MovieClip).visible = false;
			(m_pUnitOperationDownSkins[nUnitOperationIndex] as MovieClip).visible = false;
			(m_pButtonDisabledSkins[nUnitOperationIndex] as MovieClip).visible = false;
			(m_pUnitOperationDisabledSkins[nUnitOperationIndex] as MovieClip).visible = false;
			(m_pButtonActiveSkins[nUnitOperationIndex] as MovieClip).visible = true;
			(m_pUnitOperationActiveSkins[nUnitOperationIndex] as MovieClip).visible = true;

			// Set the unit operation label colors
			(m_pUnitOperationLabels[nUnitOperationIndex] as UILabel).textColor = m_nUnitOperationActiveTextColor;
			(m_pNumberLabels[nUnitOperationIndex] as UILabel).textColor = m_nNumberActiveTextColor;
			if (m_pNoteLabels[nUnitOperationIndex] != null)
			{
				(m_pNoteLabels[nUnitOperationIndex] as UILabel).textColor = m_nNoteActiveTextColor;
			}
		}

		// Renders the specified button as release
		protected function ReleaseButton(nUnitOperationIndex:int):void
		{
			// Determine the visibility of the up, disabled and active skins and the various label colors
			var bUpVisible:Boolean = false, bDisabledVisible:Boolean = false, bActiveVisible:Boolean = false;
			var nUnitOperationLabelColor:uint = 0, nNoteLabelColor:uint = 0, nNumberLabelColor:uint = 0;
			if (nUnitOperationIndex == m_nSelectedIndex)
			{
				bActiveVisible = true;
				nUnitOperationLabelColor = m_nUnitOperationActiveTextColor;
				nNoteLabelColor = m_nNoteActiveTextColor;
				nNumberLabelColor = m_nNumberActiveTextColor;
			}
			else if (m_bUnitOperationEnabled[nUnitOperationIndex])
			{
				bUpVisible = true;
				nUnitOperationLabelColor = m_nUnitOperationEnabledTextColor;
				nNoteLabelColor = m_nNoteEnabledTextColor;
				nNumberLabelColor = m_nNumberEnabledTextColor;
			}
			else
			{
				bDisabledVisible = true;
				nUnitOperationLabelColor = m_nUnitOperationDisabledTextColor;
				nNoteLabelColor = m_nNoteDisabledTextColor;
				nNumberLabelColor = m_nNumberDisabledTextColor;
			}
			
			// Show the skin
			(m_pButtonUpSkins[nUnitOperationIndex] as MovieClip).visible = bUpVisible;
			(m_pUnitOperationUpSkins[nUnitOperationIndex] as MovieClip).visible = bUpVisible;
			(m_pButtonDownSkins[nUnitOperationIndex] as MovieClip).visible = false;
			(m_pUnitOperationDownSkins[nUnitOperationIndex] as MovieClip).visible = false;
			(m_pButtonDisabledSkins[nUnitOperationIndex] as MovieClip).visible = bDisabledVisible;
			(m_pUnitOperationDisabledSkins[nUnitOperationIndex] as MovieClip).visible = bDisabledVisible;
			(m_pButtonActiveSkins[nUnitOperationIndex] as MovieClip).visible = bActiveVisible;
			(m_pUnitOperationActiveSkins[nUnitOperationIndex] as MovieClip).visible = bActiveVisible;

			// Set the label colors
			(m_pUnitOperationLabels[nUnitOperationIndex] as UILabel).textColor = nUnitOperationLabelColor;
			if (m_pNoteLabels[nUnitOperationIndex] != null)
			{
				(m_pNoteLabels[nUnitOperationIndex] as UILabel).textColor = nNoteLabelColor;
			}
			(m_pNumberLabels[nUnitOperationIndex] as UILabel).textColor = nNumberLabelColor;
		}
		
		// Add a skin
		protected function AddSkin(pClass:Class, pParent:Sprite = null):MovieClip
		{
			var pSkin:MovieClip = new pClass() as MovieClip;
			pSkin.buttonMode = false;
			if (pParent != null)
			{
				pParent.addChild(pSkin);
			}
			else
			{
				(_slider as Form).addChild(pSkin);
			}
			return pSkin;
		}

		// Add a skin from a string of the class name
		protected function AddSkinFromString(sClass:String):MovieClip
		{
			return AddSkin(getDefinitionByName(sClass) as Class);
		}

		// Create a new text label
		protected function AddLabel(sFontFace:String, nFontSize:int, nTextColor:uint, pParent:Sprite = null):UILabel
		{
			var pXML:XML =
				<label useEmbedded="true" alignH="left" alignV="bottom">
					<font face={sFontFace} size={nFontSize} />
				</label>;
			var pLabel:UILabel = (_slider as Form).CreateLabel(pXML, attributes);
			if (pParent != null)
			{
				_slider.removeChild(pLabel);
				pParent.addChild(pLabel);
			}
			var pTextFormat:TextFormat = pLabel.getTextFormat();
			pTextFormat.align = TextFormatAlign.CENTER;
			pLabel.setTextFormat(pTextFormat);
			pLabel.textColor = nTextColor;
			pLabel.multiline = false;
			pLabel.wordWrap = false;
			return pLabel;
		}
		
		// Called when the user clicks and holds a unit operation
		protected function OnHoldTimer(event:TimerEvent):void
		{
			// Ignore if a unit operation isn't pressed
			if (m_nPressedIndex == -1)
			{
				return;
			}

			// Ignore if the mouse is not over the same unit operation that was initially pressed
			if (!(m_pHitAreas[m_nPressedIndex] as Rectangle).contains(_slider.mouseX, _slider.mouseY))
			{
				return;
			}

			// Assume control of the user's input from the base class
			stage.removeEventListener(MouseEvent.MOUSE_UP, mouseUp);
			_dragTimer.stop();
			_touchTimer.stop();
			trace("Restore base class control in SequencerBody?");

			// Get a reference to the pressed sequence component
			var nSequenceIndex:int = m_nPressedIndex + (m_pSequence.Components.length - m_pHitAreas.length);
			var pComponent:SequenceComponent = m_pSequence.Components[nSequenceIndex] as SequenceComponent;

			// Duplicate the pressed unit operation
			var pDragTarget:Sprite = new Sprite();
			stage.addChild(pDragTarget);
			var pDeleteSkin:MovieClip = AddSkin(tools_btn_delete, pDragTarget);
			pDeleteSkin.visible = false;
			var pUpSkin:MovieClip, pForegroundSkin:MovieClip, pLabel:UILabel;
			if (m_nPressedIndex == m_nSelectedIndex)
			{
				pUpSkin = AddSkin(tools_btn_active, pDragTarget);
				pForegroundSkin = AddSkin(Components.GetActiveSkin(pComponent.ComponentType), pDragTarget);
				pLabel = AddLabel(m_sUnitOperationFontFace, m_nUnitOperationFontSize, m_nUnitOperationActiveTextColor,
					pDragTarget);
			}
			else
			{
				pUpSkin = AddSkin(tools_btn_up, pDragTarget);
				pForegroundSkin = AddSkin(Components.GetUpSkin(pComponent.ComponentType), pDragTarget);
				pLabel = AddLabel(m_sUnitOperationFontFace, m_nUnitOperationFontSize, m_nUnitOperationEnabledTextColor,
					pDragTarget);
			}
			pDeleteSkin.width = pUpSkin.width = m_nButtonSkinWidth;
			pDeleteSkin.scaleY = pUpSkin.scaleY = pDeleteSkin.scaleX;
			pForegroundSkin.x = (m_nButtonSkinWidth - pForegroundSkin.width) / 2;
			pForegroundSkin.y = ICON_PADDING;
			pLabel.text = pComponent.ComponentType;
			pLabel.width = pLabel.textWidth + 5;
			pLabel.x = (m_nButtonSkinWidth - pLabel.width) / 2;
			pLabel.y = pForegroundSkin.y + pForegroundSkin.height + ICON_GAP;
			
			// Add error callout if the unit operation has one
			if (m_pUnitOperationWarningIcons[m_nPressedIndex] != null)
			{
				var pWarningIcon:MovieClip = AddSkin(sequencer_invalidMarker, pDragTarget);
				pWarningIcon.height = WARNING_ICON_HEIGHT;
				pWarningIcon.scaleX = pWarningIcon.scaleY;
				pWarningIcon.x = pUpSkin.width - pWarningIcon.width + WARNING_ICON_OFFSETX;
				pWarningIcon.y = WARNING_ICON_OFFSETY;
			}

			// Start the drag operation
			m_pSequencer.StartDraggingExisting(pDragTarget, pComponent.ID, pUpSkin, pDeleteSkin);
			
			// Clear the pressed index and hide the drag target
			m_nPressedIndex = -1;
			HideDragTarget(pComponent.ID);
		}

		// Hit test the drag target
		public function DragHitTest(pDragTarget:Sprite):void
		{
			// Check if we have a drag target
			if (pDragTarget)
			{
				// Create or close any drop opening
				var pDragTargetIDs:Array = FindDragTargetIDs(pDragTarget);
				if (pDragTargetIDs)
				{
					CreateDropOpening(pDragTargetIDs[0]);
				}
			}
			else
			{
				// Close any opening in the unit operations
				CloseDropOpening();
			}
		}

		// Called when the user drops an existing unit operation on the trash can
		public function DropOnDelete():void
		{
			// Delete the component from the sequence
			m_pScreen.DoDelete("sequence/" + m_pSequence.Metadata.ID + "/component/" + m_nDraggingID);

			// Restore the drag target and update the sequence
			UnhideDragTarget();
		}
		
		// Called when the user drops an existing unit operation
		public function DropExisting(pDragTarget:Sprite):void
		{
			// Move the existing unit operation
			var pDragTargetIDs:Array = FindDragTargetIDs(pDragTarget);
			if (pDragTargetIDs)
			{
				m_pScreen.DoPost(null, "sequence/" + m_pSequence.Metadata.ID + "/component/" + m_nDraggingID + "/" + pDragTargetIDs[0]);
			}

			// Restore the drag target and update the sequence
			UnhideDragTarget();
		}
		
		// Called when the user drops a new unit operation
		public function DropNew(pDragTarget:Sprite, sDraggingOperation:String):void
		{
			// Insert the new unit operation
			var pDragTargetIDs:Array = FindDragTargetIDs(pDragTarget);
			if (pDragTargetIDs)
			{
				// Create a blank instance of the appropriate unit operation
				var pComponentClass:Class = Components.GetComponentClass(sDraggingOperation);
				var pComponent:* = new pComponentClass();
					
				// Insert the unit operation
				m_pScreen.DoPost(pComponent, "sequence/" + m_pSequence.Metadata.ID + "/component/0/" + pDragTargetIDs[0]);
			}
		}

		// Locates the insert ID for the give drag target
		protected function FindDragTargetIDs(pDragTarget:Sprite):Array
		{
			// Search for the unit operations that intersect with the drag target
			var nIndex:int, nUnitOperationIndex:int = 0, pComponent:SequenceComponent, pReturn:Array = new Array(), 
				nLastCassetteID:int = -1, nFirstUnitOperationID:int = -1, nLastUnitOperationID:int = -1;
			var pDragRect:Rectangle = pDragTarget.getBounds(_slider);
			for (nIndex = 0; nIndex < m_pSequence.Components.length; ++nIndex)
			{
				// Skip cassettes
				pComponent = m_pSequence.Components[nIndex] as SequenceComponent;
				if (pComponent.ComponentType == ComponentCassette.COMPONENTTYPE)
				{
					// Remember the last cassette ID
					nLastCassetteID = pComponent.ID;
					continue;
				}

				// Skip the unit operation that we are dragging
				if (pComponent.ID == m_nDraggingID)
				{
					++nUnitOperationIndex;
					continue;
				}
				
				// Remember the first unit operation
				if (nFirstUnitOperationID == -1)
				{
					nFirstUnitOperationID = pComponent.ID;
				}
				
				// Hit test
				if ((m_pHitAreas[nUnitOperationIndex] as Rectangle).intersects(pDragRect))
				{
					// They intersect, add the component ID
					pReturn.push(pComponent.ID);
					
					// The drag target should only be able to overlap two unit operations
					if (pReturn.length == 2)
					{
						break;
					}
				}
				
				// Remember the last unit operation ID and increment
				nLastUnitOperationID = pComponent.ID;
				++nUnitOperationIndex;
			}

			// Prepend the last cassette ID if the only item in our array is the first unit operation ID
			if ((pReturn.length == 1) && (pReturn[0] == nFirstUnitOperationID))
			{
				pReturn[0] = nLastCassetteID;
				pReturn.push(nFirstUnitOperationID);
			}
			
			// Return the insert ID if we have one
			if (pReturn.length)
			{
				return pReturn;
			}
			
			// Return the last unit operation or cassette ID if the user dropped the unit operation
			// anywhere on the slider
			var pSliderRect:Rectangle = new Rectangle(0, 0, _slider.width, _slider.height);
			if (pSliderRect.intersects(pDragRect))
			{
				if (nLastUnitOperationID != -1)
				{
					return [nLastUnitOperationID];
				}
				else
				{
					return [nLastCassetteID];
				}
			}
			
			// Drag target was dropped elsewhere on the screen
			return null;
		}
		
		// Hides the sequencer drag target
		protected function HideDragTarget(nDragTargetID:int):void
		{
			// Remember the drag target ID
			m_nDraggingID = nDragTargetID;
			
			// Walk the component array and adjust each one
			var nIndex:int, pComponent:SequenceComponent, nUnitOperationIndex:int = 0, bFound:Boolean = false,
				nPreviousUnitOperationID:int = -1, nOpeningWidth:Number = m_nUnitOperationWidth * DROP_OPENING_PERCENT/ 100;
			for (nIndex = 0; nIndex < m_pSequence.Components.length; ++nIndex)
			{
				// Skip cassettes
				pComponent = m_pSequence.Components[nIndex] as SequenceComponent;
				if (pComponent.ComponentType == ComponentCassette.COMPONENTTYPE)
				{
					nPreviousUnitOperationID = pComponent.ID;
					continue;
				}
				
				// Skip until we get to the unit operation that is being hidden
				if (!bFound && (pComponent.ID != m_nDraggingID))
				{
					++nUnitOperationIndex;
					nPreviousUnitOperationID = pComponent.ID;
					continue;
				}
				
				// Hide the target unit operation
				if (!bFound)
				{
					// Hide the unit operation components
					(m_pButtonUpSkins[nUnitOperationIndex] as MovieClip).visible = false;
					(m_pButtonDownSkins[nUnitOperationIndex] as MovieClip).visible = false;
					(m_pButtonDisabledSkins[nUnitOperationIndex] as MovieClip).visible = false;
					(m_pButtonActiveSkins[nUnitOperationIndex] as MovieClip).visible = false;
					if (m_pUnitOperationWarningIcons[nUnitOperationIndex])
					{
						(m_pUnitOperationWarningIcons[nUnitOperationIndex] as MovieClip).visible = false;
					}
					(m_pUnitOperationUpSkins[nUnitOperationIndex] as MovieClip).visible = false;
					(m_pUnitOperationDownSkins[nUnitOperationIndex] as MovieClip).visible = false;
					(m_pUnitOperationDisabledSkins[nUnitOperationIndex] as MovieClip).visible = false;
					(m_pUnitOperationActiveSkins[nUnitOperationIndex] as MovieClip).visible = false;
					(m_pUnitOperationLabels[nUnitOperationIndex] as UILabel).visible = false;
					if (m_pNoteLabels[nUnitOperationIndex])
					{
						(m_pNoteLabels[nUnitOperationIndex] as UILabel).visible = false;
					}
					(m_pNumberLabels[nUnitOperationIndex] as UILabel).visible = false;
					
					// Set the found flag and increment the index
					bFound = true;
					++nUnitOperationIndex;
					
					// Set the drop opening ID and continue
					m_nDropOpeningID = nPreviousUnitOperationID;
					continue;
				}
				
				// Set the positions of the button skins
				(m_pButtonUpSkins[nUnitOperationIndex] as MovieClip).x -= nOpeningWidth;
				(m_pButtonDownSkins[nUnitOperationIndex] as MovieClip).x -= nOpeningWidth;
				(m_pButtonDisabledSkins[nUnitOperationIndex] as MovieClip).x -= nOpeningWidth;
				(m_pButtonActiveSkins[nUnitOperationIndex] as MovieClip).x -= nOpeningWidth;
				if (m_pUnitOperationWarningIcons[nUnitOperationIndex])
				{
					(m_pUnitOperationWarningIcons[nUnitOperationIndex] as MovieClip).x -= nOpeningWidth;
				}
				(m_pUnitOperationUpSkins[nUnitOperationIndex] as MovieClip).x -= nOpeningWidth;
				(m_pUnitOperationDownSkins[nUnitOperationIndex] as MovieClip).x -= nOpeningWidth;
				(m_pUnitOperationDisabledSkins[nUnitOperationIndex] as MovieClip).x -= nOpeningWidth;
				(m_pUnitOperationActiveSkins[nUnitOperationIndex] as MovieClip).x -= nOpeningWidth;
				(m_pUnitOperationLabels[nUnitOperationIndex] as UILabel).x -= nOpeningWidth;
				if (m_pNoteLabels[nUnitOperationIndex])
				{
					(m_pNoteLabels[nUnitOperationIndex] as UILabel).x -= nOpeningWidth;
				}
				(m_pNumberLabels[nUnitOperationIndex] as UILabel).x -= nOpeningWidth;
				(m_pHitAreas[nUnitOperationIndex] as Rectangle).x -= nOpeningWidth;
				
				// Increment index
				++nUnitOperationIndex;
			}				
			
			// Update the slider and skins
			if ((m_pWindowRightSkin.x + m_pWindowRightSkin.width - m_nUnitOperationWidth) > attributes.width)
			{
				// Update the center and right window skin positions
				m_pWindowRightSkin.x -= m_nUnitOperationWidth;
				m_pWindowCenterSkin.width -= m_nUnitOperationWidth;
				
				// Reduce the slider dimensions
				var pSlider:Form = _slider as Form;
				pSlider.ForceWidth(pSlider.attributes.width - m_nUnitOperationWidth);
				doLayout();
			}
		}

		// Unhides the sequencer drag target
		protected function UnhideDragTarget():void
		{
			// Walk the component array and restore the hidden unit operation
			var nIndex:int, pComponent:SequenceComponent, nUnitOperationIndex:int = 0;
			for (nIndex = 0; nIndex < m_pSequence.Components.length; ++nIndex)
			{
				// Skip cassettes
				pComponent = m_pSequence.Components[nIndex] as SequenceComponent;
				if (pComponent.ComponentType == ComponentCassette.COMPONENTTYPE)
				{
					continue;
				}
				
				// Skip until we get to the unit operation that was hidden
				if (pComponent.ID != m_nDraggingID)
				{
					++nUnitOperationIndex;
					continue;
				}
				
				// Unhide the target unit operation
				(m_pButtonUpSkins[nUnitOperationIndex] as MovieClip).visible = true;
				(m_pButtonDownSkins[nUnitOperationIndex] as MovieClip).visible = true;
				(m_pButtonDisabledSkins[nUnitOperationIndex] as MovieClip).visible = true;
				(m_pButtonActiveSkins[nUnitOperationIndex] as MovieClip).visible = true;
				if (m_pUnitOperationWarningIcons[nUnitOperationIndex])
				{
					(m_pUnitOperationWarningIcons[nUnitOperationIndex] as MovieClip).visible = true;
				}
				(m_pUnitOperationUpSkins[nUnitOperationIndex] as MovieClip).visible = true;
				(m_pUnitOperationDownSkins[nUnitOperationIndex] as MovieClip).visible = true;
				(m_pUnitOperationDisabledSkins[nUnitOperationIndex] as MovieClip).visible = true;
				(m_pUnitOperationActiveSkins[nUnitOperationIndex] as MovieClip).visible = true;
				(m_pUnitOperationLabels[nUnitOperationIndex] as UILabel).visible = true;
				if (m_pNoteLabels[nUnitOperationIndex])
				{
					(m_pNoteLabels[nUnitOperationIndex] as UILabel).visible = true;
				}
				(m_pNumberLabels[nUnitOperationIndex] as UILabel).visible = true;
			}
			
			// Clear the dragging IDs and refresh the sequence
			m_nDraggingID = -1;
			m_nDropOpeningID = -1;
			UpdateSequence(m_pSequence);
		}
		
		// Creates a drop opening after the specified unit operation
		protected function CreateDropOpening(nFirstUnitOperationID:int):void
		{
			/*
			// Ignore if the unit operation hasn't changed
			if (nFirstUnitOperationID == m_nDropOpeningID)
			{
				return;
			}
			
			// Walk the component array and adjust each one
			var nIndex:int, pComponent:SequenceComponent, nUnitOperationIndex:int = 0, nDeltaX:Number = 0;
			for (nIndex = 0; nIndex < m_pSequence.Components.length; ++nIndex)
			{
				// Check if the is the existing drop opening
				pComponent = m_pSequence.Components[nIndex] as SequenceComponent;
				if (pComponent.ID == m_nDropOpeningID)
				{
					trace("existing site");
				}
				
				// Check if this is the site of the new drop opening
				if (pComponent.ID == nFirstUnitOperation)
				{
					trace("new site");
				}
				
				// Skip cassettes
				if (pComponent.ComponentType == ComponentCassette.COMPONENTTYPE)
				{
					continue;
				}

				// Set the positions of the button skins
				(m_pButtonUpSkins[nUnitOperationIndex] as MovieClip).x += nDeltaX;
				(m_pButtonDownSkins[nUnitOperationIndex] as MovieClip).x -= nDeltaX;
				(m_pButtonDisabledSkins[nUnitOperationIndex] as MovieClip).x -= nDeltaX;
				(m_pButtonActiveSkins[nUnitOperationIndex] as MovieClip).x -= nDeltaX;
				if (m_pUnitOperationWarningIcons[nUnitOperationIndex])
				{
					(m_pUnitOperationWarningIcons[nUnitOperationIndex] as MovieClip).x -= nDeltaX;
				}
				(m_pUnitOperationUpSkins[nUnitOperationIndex] as MovieClip).x -= nDeltaX;
				(m_pUnitOperationDownSkins[nUnitOperationIndex] as MovieClip).x -= nDeltaX;
				(m_pUnitOperationDisabledSkins[nUnitOperationIndex] as MovieClip).x -= nDeltaX;
				(m_pUnitOperationActiveSkins[nUnitOperationIndex] as MovieClip).x -= nDeltaX;
				(m_pUnitOperationLabels[nUnitOperationIndex] as UILabel).x -= nDeltaX;
				if (m_pNoteLabels[nUnitOperationIndex])
				{
					(m_pNoteLabels[nUnitOperationIndex] as UILabel).x -= nDeltaX;
				}
				(m_pNumberLabels[nUnitOperationIndex] as UILabel).x -= nDeltaX;
				(m_pHitAreas[nUnitOperationIndex] as Rectangle).x -= nDeltaX;
				
				// Increment index
				++nUnitOperationIndex;
			}				
			
			// Update the slider and skins
			if ((m_pWindowRightSkin.x + m_pWindowRightSkin.width - m_nUnitOperationWidth) > attributes.width)
			{
				// Update the center and right window skin positions
				m_pWindowRightSkin.x -= m_nUnitOperationWidth;
				m_pWindowCenterSkin.width -= m_nUnitOperationWidth;
				
				// Reduce the slider dimensions
				var pSlider:Form = _slider as Form;
				pSlider.ForceWidth(pSlider.attributes.width - m_nUnitOperationWidth);
				doLayout();
			}
			*/
			
			// Remember the drop opening
			m_nDropOpeningID = nFirstUnitOperationID;
		}

		// Closes any drop opening
		protected function CloseDropOpening():void
		{
			if (m_nDropOpeningID != -1)
			{
				trace("close opening: " + m_nDropOpeningID);
				m_nDropOpeningID = -1;
			}
		}

		/***
		 * Member variables
		 **/

		// Sequencer XML
		protected static const SEQUENCERBODY:XML = 
			<frame border="false" />;

		// Input parameters
		protected var m_sMode:String = "";
		protected var m_sUnitOperationFontFace:String = "";
		protected var m_nUnitOperationFontSize:int = 0;
		protected var m_nUnitOperationEnabledTextColor:uint = 0;
		protected var m_nUnitOperationDisabledTextColor:uint = 0;
		protected var m_nUnitOperationActiveTextColor:uint = 0;
		protected var m_nUnitOperationPressedTextColor:uint = 0;
		protected var m_sNoteFontFace:String = "";
		protected var m_nNoteFontSize:int = 0;
		protected var m_nNoteEnabledTextColor:uint = 0;
		protected var m_nNoteDisabledTextColor:uint = 0;
		protected var m_nNoteActiveTextColor:uint = 0;
		protected var m_sNumberFontFace:String = "";
		protected var m_nNumberFontSize:int = 0;
		protected var m_nNumberEnabledTextColor:uint = 0;
		protected var m_nNumberDisabledTextColor:uint = 0;
		protected var m_nNumberActiveTextColor:uint = 0;
		protected var m_nNumberActiveBackgroundColor:uint = 0;

		// Components
		protected var m_pWindowLeftSkin:MovieClip;
		protected var m_pWindowCenterSkin:MovieClip;
		protected var m_pWindowRightSkin:MovieClip;
		protected var m_pButtonUpSkins:Array = new Array();
		protected var m_pButtonDownSkins:Array = new Array();
		protected var m_pButtonDisabledSkins:Array = new Array();
		protected var m_pButtonActiveSkins:Array = new Array();
		protected var m_pUnitOperationUpSkins:Array = new Array();
		protected var m_pUnitOperationDownSkins:Array = new Array();
		protected var m_pUnitOperationDisabledSkins:Array = new Array();
		protected var m_pUnitOperationActiveSkins:Array = new Array();
		protected var m_pUnitOperationWarningIcons:Array = new Array();
		protected var m_bUnitOperationEnabled:Array = new Array();
		protected var m_pUnitOperationLabels:Array = new Array();
		protected var m_pNoteLabels:Array = new Array();
		protected var m_pNumberLabels:Array = new Array();
		
		// Dimensions
		protected var m_nUnitOperationWidth:Number = 0;
		protected var m_nSequencerWindowHeight:Number = 0;
		protected var m_nButtonSkinWidth:Number = 0;
		
		// Sequencer and screen
		protected var m_pSequencer:Sequencer;
		protected var m_pScreen:Screen;
		
		// Current sequence and selected component ID
		protected var m_pSequence:Sequence;
		protected var m_nSelectedComponentID:int = -1;
		
		// Unit operation hit areas
		protected var m_pHitAreas:Array = new Array();
		protected var m_nSelectedIndex:int = -1;
		protected var m_nPressedIndex:int = -1;
		
		// Drag and drop variables
		protected var m_pHoldTimer:Timer;
		protected var m_nDraggingID:int = -1;
		protected var m_nDropOpeningID:int = -1;
				
		// Constants
		public static var WARNING_ICON_HEIGHT:int = 15;
		public static var WARNING_ICON_OFFSETX:int = 4;
		public static var WARNING_ICON_OFFSETY:int = -4;
		public static var NOTE_GAP:int = 5;
		public static var ICON_PADDING:int = 6;
		public static var ICON_GAP:int = 2;
		public static var TEXT_HEIGHT:int = 12;
		public static var WINDOW_GAP:int = 20;
		public static var WINDOW_PERCENT_HEIGHT:int = 77;
		public static var BUTTON_PERCENT_UPPER_GAP:int = 15;
		public static var BUTTON_PERCENT_LOWER_GAP:int = 36;
		public static var SELECTED_GAP:int = 3;
		public static var SELECTED_NUMBER_CURVE:int = 10;
		public static var DROP_OPENING_PERCENT:int = 60;
	}
}
