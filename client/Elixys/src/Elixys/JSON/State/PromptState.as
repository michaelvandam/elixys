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
		
		// State components
		protected var m_pButtons:Array;
	}
}
