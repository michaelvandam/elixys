package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class PromptState extends JSONObject
	{
		// Constructor
		public function PromptState(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Static type
		public static function get TYPE():String
		{
			return "promptstate";
		}

		// Data wrappers
		public function get Show():Boolean
		{
			return super.flash_proxy::getProperty("show");
		}
		public function get Title():String
		{
			return super.flash_proxy::getProperty("title");
		}
		public function get Text1():String
		{
			return super.flash_proxy::getProperty("text1");
		}
		public function get Edit1():Boolean
		{
			return super.flash_proxy::getProperty("edit1");
		}
		public function get Edit1Default():String
		{
			return super.flash_proxy::getProperty("edit1default");
		}
		public function get Edit1Validation():String
		{
			return super.flash_proxy::getProperty("edit1validation");
		}
		public function get Text2():String
		{
			return super.flash_proxy::getProperty("text2");
		}
		public function get Edit2():Boolean
		{
			return super.flash_proxy::getProperty("edit2");
		}
		public function get Edit2Default():String
		{
			return super.flash_proxy::getProperty("edit2default");
		}
		public function get Edit2Validation():String
		{
			return super.flash_proxy::getProperty("edit2validation");
		}
		public function get Buttons():Array
		{
			// Parse the buttons
			if (m_pButtons == null)
			{
				m_pButtons = new Array();
				var pButtons:Array = super.flash_proxy::getProperty("buttons");
				for each (var pButtonObject:Object in pButtons)
				{
					var pButton:Button = new Button(null, pButtonObject);
					m_pButtons.push(pButton);
				}
			}
			return m_pButtons;
		}
		
		// Prompt state comparison function.  Returns true if the prompt states are equal, false otherwise.
		public static function ComparePromptStates(pPromptA:PromptState, pPromptB:PromptState):Boolean
		{
			if (pPromptA.Show != pPromptB.Show)
			{
				return false;
			}
			if (pPromptA.Title != pPromptB.Title)
			{
				return false;
			}
			if (pPromptA.Text1 != pPromptB.Text1)
			{
				return false;
			}
			if (pPromptA.Edit1 != pPromptB.Edit1)
			{
				return false;
			}
			if (pPromptA.Edit1Default != pPromptB.Edit1Default)
			{
				return false;
			}
			if (pPromptA.Edit1Validation != pPromptB.Edit1Validation)
			{
				return false;
			}
			if (pPromptA.Text2 != pPromptB.Text2)
			{
				return false;
			}
			if (pPromptA.Edit2 != pPromptB.Edit2)
			{
				return false;
			}
			if (pPromptA.Edit2Default != pPromptB.Edit2Default)
			{
				return false;
			}
			if (pPromptA.Edit2Validation != pPromptB.Edit2Validation)
			{
				return false;
			}
			return Button.CompareButtonArrays(pPromptA.Buttons, pPromptB.Buttons);
		}

		// State components
		protected var m_pButtons:Array;
	}
}
