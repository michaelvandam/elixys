package Elixys.Subviews
{
	import Elixys.Assets.*;
	import Elixys.Components.CheckBox;
	import Elixys.Components.Screen;
	import Elixys.Events.CheckBoxEvent;
	import Elixys.Extended.Form;
	import Elixys.Extended.Input;
	import Elixys.Interfaces.ITextBox;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.State.Reagent;
	import Elixys.JSON.State.Reagents;
	import Elixys.JSON.State.RunState;
	import Elixys.JSON.State.Sequence;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObjectContainer;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.FocusEvent;
	import flash.events.KeyboardEvent;
	import flash.events.SoftKeyboardEvent;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.getQualifiedClassName;
	

	// This subview baset is an extension of our extended Form class
	public class SubviewBase extends Form
	{
		/***
		 * Construction
		 **/
		
		public function SubviewBase(screen:Sprite, sMode:String, pElixys:Elixys, sSubviewType:String, 
									nButtonWidth:Number, pViewXML:XML, pEditXML:XML, pRunXML:XML,
									attributes:Attributes)
		{
			// Remember the mode, elixys and subview type
			m_sMode = sMode;
			m_pElixys = pElixys;
			m_sSubviewType = sSubviewType;

			// Call the base constructor
			var pXML:XML;
			switch (m_sMode)
			{
				case Constants.VIEW:
					pXML = pViewXML;
					break;
				
				case Constants.EDIT:
					pXML = pEditXML;
					break;
				
				case Constants.RUN:
					pXML = pRunXML;
					break;
			}
			super(screen, pXML, attributes);
			
			// Start invisible
			visible = false;
		}

		/***
		 * Member functions
		 **/

		// Updates the sequence
		public function UpdateSequence(pSequence:Sequence):void
		{
			// Remember the sequence
			m_pSequence = pSequence;
		}

		// Updates the component
		public function UpdateComponent(pComponent:ComponentBase):void
		{
		}
		
		// Updates the run state
		public function UpdateRunState(pRunState:RunState):void
		{
			m_pRunState = pRunState;
		}
		
		// Updates the reagent list
		public function UpdateReagents(pReagents:Reagents):void
		{
		}
		
		// Returns the subview type
		public function get SubviewType():String
		{
			return m_sSubviewType;
		}

		// Adds an input
		protected function AddInput(nFontSize:int, sFontColor:String, sReturnKeyLabel:String, pParent:Sprite = null):Input
		{
			var pXML:XML =
				<input size={nFontSize} alignH="fill" color={sFontColor} 
					skin={getQualifiedClassName(TextInput_upSkin)} 
					returnKeyLabel={sReturnKeyLabel} />;
			var pInput:Input = CreateInput(pXML, attributes, pParent);
			return pInput;
		}

		// Adds a skinless input
		protected function AddSkinlessInput(nFontSize:int, sFontColor:String, sReturnKeyLabel:String, pParent:Sprite = null):Input
		{
			var pXML:XML =
				<input size={nFontSize} alignH="fill" color={sFontColor} 
					returnKeyLabel={sReturnKeyLabel} />;
			var pInput:Input = CreateInput(pXML, attributes, pParent);
			var pTextBox:ITextBox = pInput.inputField as ITextBox;
			pTextBox.borderColor = 0xFFFFFF;
			pTextBox.textAlign = "right";
			return pInput;
		}
		
		// Adds an multiline input
		protected function AddMultilineInput(nFontSize:int, sFontColor:String, nLines:int, pParent:Sprite = null):Input
		{
			var pXML:XML =
				<input size={nFontSize} alignH="fill" color={sFontColor} 
					skin={getQualifiedClassName(TextInput_upSkin)} />;
			return CreateMultilineInput(pXML, attributes, nLines, pParent);
		}

		// Adds a skinless multiline input
		protected function AddSkinlessMultilineInput(nFontSize:int, sFontColor:String, nLines:int, pParent:Sprite = null):Input
		{
			var pXML:XML =
				<input size={nFontSize} alignH="fill" color={sFontColor} />;
			var pInput:Input = CreateMultilineInput(pXML, attributes, nLines, pParent);
			var pTextBox:ITextBox = pInput.inputField as ITextBox;
			pTextBox.borderColor = 0xFFFFFF;
			pTextBox.textAlign = "right";
			return pInput;
		}

		// Adds a check box
		protected function AddCheckBox(pParent:Sprite = null):CheckBox
		{
			if (!pParent)
			{
				pParent = this;
			}
			return new CheckBox(pParent, null, attributes);
		}

		// Configures the given text box
		protected function ConfigureTextBox(pTextBox:ITextBox):void
		{
			pTextBox.addEventListener(FocusEvent.FOCUS_IN, OnTextFocusIn);
			pTextBox.addEventListener(FocusEvent.FOCUS_OUT, OnTextFocusOut);
			pTextBox.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_ACTIVATE, OnKeyboardChange);
			pTextBox.addEventListener(SoftKeyboardEvent.SOFT_KEYBOARD_DEACTIVATE, OnKeyboardChange);
			pTextBox.addEventListener(KeyboardEvent.KEY_DOWN, OnKeyboardDown);
			m_pTextBoxTabOrder.push(pTextBox);
		}

		// Configures the given check box
		protected function ConfigureCheckBox(pCheckBox:CheckBox):void
		{
			pCheckBox.addEventListener(CheckBoxEvent.CHANGE, OnCheckBoxChanged);
		}

		// Called when a text control receives focus
		public function OnTextFocusIn(event:FocusEvent):void
		{
			// Determine which input has the keyboard focus
			var pTextBox:ITextBox = FindTextBox(event.target);
			if (pTextBox != null)
			{
				m_pKeyboardFocusTextBox = pTextBox;
				m_sKeyboardFocusInitialText = m_pKeyboardFocusTextBox.text;
			}
		}
		
		// Called when a text control loses focus
		public function OnTextFocusOut(event:FocusEvent):void
		{
			if (m_pKeyboardFocusTextBox != null)
			{
				// Has the value of the text input changed?
				if (m_pKeyboardFocusTextBox.text != m_sKeyboardFocusInitialText)
				{
					// Yes, so update and save the component
					OnTextValueChanged(m_pKeyboardFocusTextBox);
				}
				
				// Clear our pointer
				m_pKeyboardFocusTextBox = null;
			}
		}
		
		// Overridden in derived classes to handle when the user changes the text in one of our input fields
		protected function OnTextValueChanged(pFocusTarget:ITextBox):void
		{
		}

		// Overridden in derived classes to handle when the user changes the state of a check box
		protected function OnCheckBoxChanged(event:CheckBoxEvent):void
		{
		}

		// Called when the soft keyboard actives or deactivates
		protected function OnKeyboardChange(event:SoftKeyboardEvent):void
		{
			// Pan the application
			m_pElixys.PanApplication(m_nInputAreaOfInterestTop, m_nInputAreaOfInterestBottom);
		}
		
		// Called when a text box receives a key down event
		protected function OnKeyboardDown(event:KeyboardEvent):void
		{
			// Locate the text box and check if it is a single or multiline input control
			var pTextBox:ITextBox = FindTextBox(event.target);
			var bMoveFocus:Boolean = false;
			if (pTextBox)
			{
				if (pTextBox.maxNumberOfLines > 1)
				{
					// For multiline inputs the tab moves the focus to the next field in the tab order
					if (event.keyCode == Constants.CHAR_TAB)
					{
						bMoveFocus = true;
					}
				}
				else
				{
					// For single line inputs either tab or return moves the focus to the next field in the tab order
					if ((event.keyCode == Constants.CHAR_TAB) || (event.keyCode == Constants.CHAR_RETURN))
					{
						bMoveFocus = true;
					}
				}
			}
			
			// Move the focus to the next text box
			if (bMoveFocus)
			{
				event.preventDefault();
				pTextBox = FindNextTextBox(event.target);
				if (pTextBox)
				{
					pTextBox.assignFocus();
				}
			}
		}

		// Finds the text box that contains the specified target
		protected function FindTextBox(pTarget:Object):ITextBox
		{
			var nIndex:int, pTextBox:ITextBox;
			for (nIndex = 0; nIndex < m_pTextBoxTabOrder.length; ++nIndex)
			{
				pTextBox = m_pTextBoxTabOrder[nIndex] as ITextBox;
				if (pTextBox.containsInternally(pTarget))
				{
					return pTextBox;
				}
			}
			return null;
		}

		// Finds the text box after the one that contains the specified target
		protected function FindNextTextBox(pTarget:Object):ITextBox
		{
			var nIndex:int, pTextBox:ITextBox;
			for (nIndex = 0; nIndex < m_pTextBoxTabOrder.length; ++nIndex)
			{
				pTextBox = m_pTextBoxTabOrder[nIndex] as ITextBox;
				if (pTextBox.containsInternally(pTarget))
				{
					if ((nIndex + 1) < m_pTextBoxTabOrder.length)
					{
						return (m_pTextBoxTabOrder[nIndex + 1] as ITextBox);
					}
					else
					{
						return (m_pTextBoxTabOrder[0] as ITextBox);
					}
				}
			}
			return null;
		}

		// Gets the array of reagents
		protected function GetReagents(pReagents:Array):void
		{
			if (pReagents.length > 0)
			{
				var sURL:String = "sequence/" + m_pSequence.Metadata.ID + "/reagent/" + pReagents[0];
				for (var nIndex:int = 1; nIndex < pReagents.length; ++nIndex)
				{
					sURL += "." + pReagents[nIndex];
				}
				FindScreen().DoGet(sURL);
			}
		}
		
		// Post the component to the server
		protected function PostComponent(pComponent:ComponentBase):void
		{
			FindScreen().DoPost(pComponent, "sequence/" + m_pSequence.Metadata.ID + "/component/" + pComponent.ID);
		}

		// Post the reagent to the server
		protected function PostReagent(pReagent:Reagent):void
		{
			FindScreen().DoPost(pReagent, "sequence/" + m_pSequence.Metadata.ID + "/reagent/" + pReagent.ReagentID);
		}
		
		// Locates the screen
		protected function FindScreen():Screen
		{
			// Locate the screen
			var pParent:DisplayObjectContainer = this;
			while (pParent != null)
			{
				if (pParent is Screen)
				{
					return (pParent as Screen);
				}
				pParent = pParent.parent;
			}
			return null;
		}			
		
		/***
		 * Member variables
		 **/

		// Input parameters
		protected var m_sMode:String;
		protected var m_pElixys:Elixys;
		protected var m_sSubviewType:String;
		protected var m_nButtonWidth:Number;
		
		// Current run state and sequence
		protected var m_pRunState:RunState;
		protected var m_pSequence:Sequence;
		
		// Keyboard variables
		protected var m_pKeyboardFocusTextBox:ITextBox;
		protected var m_sKeyboardFocusInitialText:String = "";
		protected var m_nInputAreaOfInterestTop:uint;
		protected var m_nInputAreaOfInterestBottom:uint;
		protected var m_pTextBoxTabOrder:Array = new Array();
	}
}
